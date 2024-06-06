import json

import torch
import os
from torch.utils.data import random_split


def create_qa_train_test_split(file_path: str, split: float = 0.6):
    with open(file_path, encoding="utf8") as f:
        abs_path = os.path.abspath(file_path)
        root_path = os.path.dirname(abs_path)
        print(f"root path: {root_path}")
        json_data = json.load(f)
        if 'data' in json_data and isinstance(json_data['data'], list):
            question_ids = list_question_ids(json_data)
            train_size = int(len(question_ids) * split)
            test_size = len(question_ids) - train_size
            generator = torch.Generator().manual_seed(42)
            train_ids, test_ids = random_split(question_ids, [train_size, test_size], generator=generator)
            intersection = set(train_ids).intersection(set(test_ids))
            print(f"the intersection has size {len(intersection)}")
            train_data = filter_questions_by_id(file_path, list(train_ids), split_name="train")
            test_data = filter_questions_by_id(file_path, list(test_ids), split_name="test")
            with open(f"{root_path}/train.json", "w", encoding="utf8") as train_file:
                json.dump(train_data, train_file, indent=4, ensure_ascii=False)
            with open(f"{root_path}/test.json", "w", encoding="utf8") as test_file:
                json.dump(test_data, test_file, indent=4, ensure_ascii=False)


def filter_questions_by_id(file_path: dict, question_ids: list[str], split_name: str):
    with open(file_path, encoding="utf8") as f:
        data = json.load(f)
        for item in data['data']:
            if 'paragraphs' in item and isinstance(item['paragraphs'], list):
                for paragraph in item['paragraphs']:
                    if 'qas' in paragraph and isinstance(paragraph['qas'], list):
                        new_qas = []
                        for qa in paragraph['qas']:
                            print(f"is {qa['id']} in questions_ids? {str(qa['id']) in question_ids}")
                            if str(qa['id']) in question_ids:
                                new_qas.append(qa)
                        print(f"inserting qas with ids {[qa['id'] for qa in new_qas]} for split {split_name}")
                        paragraph['qas'] = new_qas
                        print(f"paragraph['qas'] size: {len(paragraph['qas'])} for split {split_name}")
    return data


def list_question_ids(data: dict) -> list[str]:
    question_ids = []
    for item in data['data']:
        if 'paragraphs' in item and isinstance(item['paragraphs'], list):
            for paragraph in item['paragraphs']:
                if 'qas' in paragraph and isinstance(paragraph['qas'], list):
                    for qa in paragraph['qas']:
                        if 'id' in qa:
                            question_ids.append(qa['id'])
    return question_ids
