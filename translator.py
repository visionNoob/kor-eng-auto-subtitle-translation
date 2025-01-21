import os
import sys
import json
import openai
from openai import OpenAI
import re
from dotenv import load_dotenv
from typing import List, Generator
import tqdm
import logging
import shared
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Translator:
    def __init__(self, client: OpenAI, lines: List[str]):
        self.client = client
        self.lines = lines
        self.subtitles = self.split_srt_into_subtitles(lines)
        pass

    def translate_subtitle_block(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        reference_str: str,
    ) -> List[str]:
        """
        Translates multiple subtitle blocks using the OpenAI API in batch, while preserving
        sequence numbers, time ranges, and empty lines.

        Args:
            blocks (List[List[str]]): List of subtitle blocks to translate.
            model (str): The model to use for translation.
            system_prompt (str): The system prompt to guide translation.
            user_prompt (str): The user prompt to guide translation.

        Returns:
            List[List[str]]: Translated subtitle blocks.
        """

        # Batch request to the translation API
        response = self.create_chat_completion_request(
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            text=reference_str,
        )
        translated_text = response.choices[0].message.content.strip()

        # Split the translated text back into lines
        # translated_lines = translated_text.split("\n")

        return translated_text

    def create_chat_completion_request(
        self, model: str, system_prompt: str, user_prompt: str, text: str
    ):
        """
        Example of combining system/user prompts with context (both English + previously translated Korean).
        """
        # system_prompt 에 extra_instruction 을 덧붙인다.
        system_content = system_prompt + "\n\n"  # 구분용 공백
        # text = "".join( ["".join(x) for x in self.subtitles][:10])
        messages = [
            {"role": "system", "content": system_content},
            {
                "role": "user",
                "content": (f"{user_prompt}\n\n" f"\n{text}"),
            },
        ]
        #
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.1,
        )

    def merge_subtitles(self, subtitles: List[List[str]]) -> List[str]:
        """
        Merges a list of subtitle blocks back into a single list of SRT lines.

        Args:
            subtitles (List[List[str]]): List of subtitle blocks.

        Returns:
            List[str]: Merged list of all SRT lines.
        """
        merged_lines = []
        for sub in subtitles:
            merged_lines.extend(sub)
            merged_lines.append("\n")

        # merge to single string
        merged_lines = "".join(merged_lines)
        return merged_lines

    def parse_subtitle_to_list(self, subtitle_text):
        """
        Parse subtitle text into a list of lists where each sublist contains:
        [index, time_range, text]
        Each element includes a trailing newline as required.

        :param subtitle_text: str, subtitle content in SRT format
        :return: list of lists, formatted subtitle entries
        """
        # Split the text by lines
        lines = subtitle_text.split("\n")

        # Initialize variables
        parsed_data = []
        temp_entry = []

        for line in lines:
            if line.isdigit():  # Start of a new entry
                if temp_entry:
                    parsed_data.append(temp_entry)
                temp_entry = [line + "\n"]  # Add index with a newline
            elif "-->" in line:  # Time range line
                temp_entry.append(line + "\n")  # Add time range with a newline
            else:  # Text content
                if len(temp_entry) < 3:
                    temp_entry.append(line + "\n")  # First line of content
                else:
                    temp_entry[2] += line + "\n"  # Append additional content lines

        # Append the last entry if it exists
        if temp_entry:
            parsed_data.append(temp_entry)

        return parsed_data

    def translate(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        progress=tqdm,
        batch_size: int = 10,
    ):
        """
        Translate subtitles using batch processing.

        Args:
            model (str): The model to use for translation.
            system_prompt (str): The system prompt to guide translation.
            user_prompt (str): The user prompt to guide translation.
            batch_size (int): The number of subtitle blocks to process per batch.
            progress (tqdm): Progress bar (default: tqdm).

        Returns:
            Merged subtitles after translation.
        """
        # Prepare the results container
        translated_blocks = self.subtitles

        # Split the subtitles into batches
        for start_idx in progress.tqdm(range(0, len(self.subtitles), batch_size)):

            # Determine the end index of the current batch
            end_idx = min(start_idx + batch_size, len(self.subtitles))
            reference_str = "".join(
                ["".join(x) for x in self.subtitles[start_idx:end_idx]]
            )

            # Translate the current batch of subtitles
            translated_batch = self.translate_subtitle_block(
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                reference_str=reference_str,
            )
            translated_batch = self.parse_subtitle_to_list(translated_batch)
            # Store the translated results in the correct indices
            for batch_idx, translated_block in enumerate(translated_batch):
                translated_blocks[start_idx + batch_idx] = translated_block

        # Merge all translated subtitle blocks
        return self.merge_subtitles(translated_blocks)

    def split_srt_into_subtitles(self, lines: List[str]) -> List[List[str]]:
        """
        Splits a list of SRT lines into subtitle blocks.

        Each block typically contains:
        - A sequence number (e.g., "1")
        - A time range (e.g., "00:00:00,000 --> 00:00:05,000")
        - One or more lines of dialogue
        - A blank line (separator)

        Args:
            lines (List[str]): The entire SRT file lines.

        Returns:
            List[List[str]]: A list of subtitle blocks, where each block is itself a list of lines.
        """
        subtitles = []
        current_sub = []

        for line in lines:
            if line.strip() == "" and current_sub:
                subtitles.append(current_sub)
                current_sub = []
            else:
                current_sub.append(line)

        # Handle the last block if it exists
        if current_sub:
            subtitles.append(current_sub)

        return subtitles
