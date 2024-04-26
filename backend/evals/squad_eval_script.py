'''
Official evaluation script for the SQuAD dataset. Version 1.
modified to return em, f1, precision, recall
'''

from collections import Counter
import json


class Evaluator(object):
    def __init__(self, path=None, articles=None, restrict_to_titles=None):
        """
        Specify either path or articles. Path should point to the JSON file
        downloaded from the website. Articles is a list of articles as found
        in the data field of the file downloaded from the website.

        restrict_to_titles, if specified, should be a set of article titles.
        Only articles with those titles will be used for evaluation.
        """
        assert (path is None) != (articles is None)
        if path is not None:
            with open(path, 'r', encoding="utf-8") as fileobj:
                articles = json.loads(fileobj.read())['data']
        self._answers = {}
        for article in articles:
            if restrict_to_titles is not None and article['title'] not in restrict_to_titles:
                continue
            for paragraph in article['paragraphs']:
                for qa in paragraph['qas']:
                    answers = self._answers[qa['id']] = []
                    for answer in qa['answers']:
                        answers.append(answer['text'])

    def ExactMatch(self, predictions):
        """
        Accepts a dict from question ID to predicted answer.
        """
        total = 0
        for question_id in self._answers.keys():
            predicted_answer = predictions.get(question_id)
            if predicted_answer is not None and self.ExactMatchSingle(question_id, predicted_answer):
                total += 1

        return 100.0 * total / len(self._answers)

    def ExactMatchSingle(self, question_id, predicted_answer):
        predicted_answer = Evaluator.CleanAnswer(predicted_answer)
        for answer in self._answers[question_id]:
            if Evaluator.CleanAnswer(answer) == predicted_answer:
                return True
        return False

    WHITESPACE_AND_PUNCTUATION = {' ', '.', ',', ':', ';', '!', '?', '$', '%', '(', ')', '[', ']', '-', '`', '\'', '"'}
    ARTICLES = {'the', 'a', 'an'}

    @staticmethod
    def CleanAnswer(answer):
        answer = answer.lower()
        if isinstance(answer, str):
            answer = answer.replace(u'\u00a0', ' ')
        else:
            answer = answer.replace('\xc2\xa0', ' ')
        while len(answer) > 1 and answer[0] in Evaluator.WHITESPACE_AND_PUNCTUATION:
            answer = answer[1:]
        while len(answer) > 1 and answer[-1] in Evaluator.WHITESPACE_AND_PUNCTUATION:
            answer = answer[:-1]

        answer = answer.split()
        if len(answer) > 1 and answer[0] in Evaluator.ARTICLES:
            answer = answer[1:]
        answer = ' '.join(answer)

        return answer

    def F1(self, predictions):
        """
        Accepts a dict from question ID to predicted answer.
        """
        total_f1 = 0
        total_precision = 0
        total_recall = 0
        for question_id in self._answers.keys():
            predicted_answer = predictions.get(question_id)
            if predicted_answer is not None:
                qa_f1, qa_precision, qa_recall = self.F1Single(question_id, predicted_answer)
                total_f1 += qa_f1
                total_precision += qa_precision
                total_recall += qa_recall

        f1 = 100.0 * total_f1 / len(self._answers)
        precision = 100.0 * total_precision / len(self._answers)
        recall = 100.0 * total_recall / len(self._answers)
        return f1, precision, recall

    def F1Single(self, question_id, predicted_answer):
        def GetTokens(text):
            text = Evaluator.CleanAnswer(text)
            for delimeter in Evaluator.WHITESPACE_AND_PUNCTUATION:
                text = text.replace(delimeter, ' ')
            return text.split()

        f1 = 0
        max_precision = 0
        max_recall = 0
        predicted_answer_tokens = Counter(GetTokens(predicted_answer))
        num_predicted_answer_tokens = sum(predicted_answer_tokens.values())
        for answer in self._answers[question_id]:
            answer_tokens = Counter(GetTokens(answer))
            num_answer_tokens = sum(answer_tokens.values())
            num_same = sum((predicted_answer_tokens & answer_tokens).values())
            if num_same == 0:
                continue
            precision = 1.0 * num_same / num_predicted_answer_tokens
            recall = 1.0 * num_same / num_answer_tokens
            max_recall = max(max_recall, recall)
            max_precision = max(max_precision, precision)
            f1 = max(2 * precision * recall / (precision + recall), f1)

        return f1, max_precision, max_recall

    def evaluate(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            results = json.load(f)

        preds = {result["id"]: result["pred_answer"] for result in results["data"]}
        em = self.ExactMatch(preds)
        f1, precision, recall = self.F1(preds)
        return em, f1, precision, recall

