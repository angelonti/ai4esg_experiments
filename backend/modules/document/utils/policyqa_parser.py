import json

from typing import Any

from modules.document.schemas import DocType, DocumentParsed


def get_all_policy_titles(file_path: str = "data/test.json") -> list[str]:
    list_of_titles = []
    with open(file_path) as f:
        json_data = json.load(f)
        if 'data' in json_data and isinstance(json_data['data'], list):
            for item in json_data['data']:
                if 'title' in item:
                    list_of_titles.append(item['title'])
    if len(list_of_titles) == 0:
        raise ValueError(f"Policy titles not found in {file_path}")
    return list_of_titles


def parse_policy_text_by_title(policy_title: str, file_path: str = "data/test.json") -> DocumentParsed:
    with open(file_path) as f:
        json_data = json.load(f)
        policy_data = find_policy(json_data, policy_title)
        if policy_data:
            return parse_policy(policy_data)
        else:
            raise ValueError(f"Policy title {policy_title} not found in {file_path}")


def find_policy(json_data: Any, policy_title: str) -> Any:
    if 'data' in json_data and isinstance(json_data['data'], list):
        for item in json_data['data']:
            if 'title' in item and item['title'] == policy_title:
                return item
    return None


def parse_policy(policy_data: Any) -> DocumentParsed:
    policy_text = gather_policy_text(policy_data)
    return DocumentParsed(
        title=policy_data['title'],
        text=policy_text,
        doc_type=DocType.Website,
        source=policy_data['title']
    )


def gather_policy_text(policy_data: Any) -> str:
    policy_text: str = ""
    if "paragraphs" in policy_data:
        for paragraph in policy_data["paragraphs"]:
            if "context" in paragraph:
                policy_text += f'\n{paragraph["context"]}'

    if policy_text == "":
        raise ValueError(f"Policy text not found in policy {policy_data['title']}")

    return policy_text


def calculate_avg_context_size(file_path: str) -> float:
    with open(file_path, encoding="utf8") as f:
        json_data = json.load(f)
        if 'data' in json_data and isinstance(json_data['data'], list):
            total = 0
            count = 0
            for item in json_data['data']:
                if 'paragraphs' in item and isinstance(item['paragraphs'], list):
                    for paragraph in item['paragraphs']:
                        if 'context' in paragraph:
                            total += len(paragraph['context'])
                            count += 1
            return total / count


def calculate_avg_answer_size(file_path: str):
    with open(file_path, encoding="utf8") as f:
        json_data = json.load(f)
        if 'data' in json_data and isinstance(json_data['data'], list):
            total = 0
            count = 0
            for item in json_data['data']:
                if 'paragraphs' in item and isinstance(item['paragraphs'], list):
                    for paragraph in item['paragraphs']:
                        if 'qas' in paragraph and isinstance(paragraph['qas'], list):
                            for qa in paragraph['qas']:
                                if 'answers' in qa and isinstance(qa['answers'], list):
                                    for answer in qa['answers']:
                                        if 'text' in answer:
                                            total += len(answer['text'])
                                            count += 1
            return total / count


def calculate_min_max_answer_size(file_path: str):
    with open(file_path, encoding="utf8") as f:
        json_data = json.load(f)
        if 'data' in json_data and isinstance(json_data['data'], list):
            max = 0
            min = float('inf')
            for item in json_data['data']:
                if 'paragraphs' in item and isinstance(item['paragraphs'], list):
                    for paragraph in item['paragraphs']:
                        if 'qas' in paragraph and isinstance(paragraph['qas'], list):
                            for qa in paragraph['qas']:
                                if 'answers' in qa and isinstance(qa['answers'], list):
                                    for answer in qa['answers']:
                                        if 'text' in answer:
                                            if len(answer['text']) > max:
                                                max = len(answer['text'])
                                            if len(answer['text']) < min:
                                                min = len(answer['text'])
            return min, max


def calculate_min_max_context_size(file_path: str):
    with open(file_path, encoding="utf8") as f:
        json_data = json.load(f)
        if 'data' in json_data and isinstance(json_data['data'], list):
            max = 0
            min = float('inf')
            for item in json_data['data']:
                if 'paragraphs' in item and isinstance(item['paragraphs'], list):
                    for paragraph in item['paragraphs']:
                        if 'context' in paragraph:
                            if len(paragraph['context']) > max:
                                max = len(paragraph['context'])
                            if len(paragraph['context']) < min:
                                min = len(paragraph['context'])
            return min, max


def count_answers(file_path: str):
    with open(file_path, encoding="utf8") as f:
        json_data = json.load(f)
        if 'data' in json_data and isinstance(json_data['data'], list):
            count = 0
            for item in json_data['data']:
                if 'paragraphs' in item and isinstance(item['paragraphs'], list):
                    for paragraph in item['paragraphs']:
                        if 'qas' in paragraph and isinstance(paragraph['qas'], list):
                            for qa in paragraph['qas']:
                                if 'answers' in qa and isinstance(qa['answers'], list):
                                    for answer in qa['answers']:
                                        count += 1
            return count


def count_questions(file_path: str):
    with open(file_path, encoding="utf8") as f:
        json_data = json.load(f)
        if 'data' in json_data and isinstance(json_data['data'], list):
            count = 0
            for item in json_data['data']:
                if 'paragraphs' in item and isinstance(item['paragraphs'], list):
                    for paragraph in item['paragraphs']:
                        if 'qas' in paragraph and isinstance(paragraph['qas'], list):
                            for qa in paragraph['qas']:
                                count += 1
            return count


def get_max_text_size(file_path: str):
    all_policy_titles = get_all_policy_titles(file_path)
    max_text_len = 0
    max_text_title = ""
    for title in all_policy_titles:
        policy = parse_policy_text_by_title(title, file_path)
        if len(policy.text) > max_text_len:
            max_text_len = len(policy.text)
            max_text_title = title
    return max_text_len, max_text_title
