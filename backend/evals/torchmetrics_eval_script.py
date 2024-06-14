import sys

from torchmetrics.functional.text import squad
from torchmetrics.retrieval import RetrievalMAP
from torchmetrics.retrieval import RetrievalMRR
from tqdm import tqdm
import json
import torch
import logging
from config import config

from evals.utils import normalize_text

logging.basicConfig(level=logging.DEBUG, filename=config.log_path, format="%(asctime)s %(name)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(consoleHandler)


def eval_squad_metrics(file_path: str):
    preds, targets = prepare_squad_data(file_path)
    results = squad(preds, targets)
    return results


def prepare_squad_data(file_path: str) -> tuple[list[dict], list[dict]]:
    with open(file_path, 'r', encoding="utf-8") as file:
        results_data = json.load(file)

    preds = []
    target = []

    for item in tqdm(results_data['data']):
        preds_item = {
            "prediction_text": item.get("pred_answer"),
            "id": item.get("id")
        }
        preds.append(preds_item)

        target_item = {
            "title": item.get("title"),
            "context": item.get("context", ""),
            "id": item.get("id"),
            "question": item.get("question"),
            "answers": {
                "text": [answer.get("text") for answer in item.get("answers")],
                "answer_start": [0 for _ in item.get("answers")]
            }
        }

        target.append(target_item)

    return preds, target


def eval_retrieval_metrics(file_path: str, top_k: int = 5):
    question_ids, indexes, preds, targets = prepare_retrieval_data(file_path, top_k=top_k)
    num_batches = len(question_ids)

    indexes_batches = torch.chunk(indexes, num_batches)
    preds_batches = torch.chunk(preds, num_batches)
    targets_batches = torch.chunk(targets, num_batches)

    map = RetrievalMAP(top_k=top_k)
    mrr = RetrievalMRR(top_k=top_k)

    questions_answered = 0
    question_ids_unanswered = []

    for i in tqdm(range(num_batches)):
        batch_map = map(preds_batches[i], targets_batches[i], indexes_batches[i])
        batch_mrr = mrr(preds_batches[i], targets_batches[i], indexes_batches[i])
        if targets_batches[i].sum() > 0:
            questions_answered += 1
        else:
            question_ids_unanswered.append(question_ids[i])
        logger.info(f"question_id:{question_ids[i]} MAP: {batch_map}, MRR: {batch_mrr}")

    map_value = map.compute()
    mrr_value = mrr.compute()

    answers_found_ratio = torch.tensor(questions_answered / len(question_ids))
    relevant_embeddings_ratio = torch.tensor(sum(targets) / len(targets))
    logger.info(f"questions answered: {[item for item in question_ids_unanswered]}")

    return {
        f'map@{top_k}': map_value,
        f'mrr@{top_k}': mrr_value,
        f'%Answers found@{top_k}': answers_found_ratio,
        f'%Relevant embeddings@{top_k}': relevant_embeddings_ratio
    }


def prepare_retrieval_data(file_path: str, top_k: int = 5):
    with open(file_path, 'r', encoding="utf-8") as file:
        data = json.load(file)['data']

    ids = []
    indexes = []
    preds = []
    targets = []

    logging.info(f"Preparing data for retrieval metrics")
    for i, item in tqdm(enumerate(data)):
        ids.append(item['id'])
        if len(item['relevant_embeddings']) > 0:
            for embedding in item['relevant_embeddings'][:top_k]:
                indexes.append(i)
                preds.append(embedding['score'])
                if any(answer for answer in item['answers'] if normalize_text(answer['text']) in normalize_text(embedding['text'])):
                    targets.append(True)
                else:
                    targets.append(False)
        else:
            indexes.append(i)
            preds.append(0)
            targets.append(False)

    indexes = torch.tensor(indexes)
    preds = torch.tensor(preds)
    targets = torch.tensor(targets)

    return ids, indexes, preds, targets


def calculate_answers_found_ratio(targets, question_ids, top_k: int = 5):
    answers_found = 0
    num_questions = len(question_ids)
    for i in range(num_questions):
        if sum(targets[i * top_k: (i + 1) * top_k]) > 0:
            answers_found += 1
    return torch.tensor(answers_found / num_questions)
