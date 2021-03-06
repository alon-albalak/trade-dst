from transformers import BertForTokenClassification
import torch
from tqdm import tqdm

label2id = {"B": 0,
            "I": 1,
            "L": 2,
            "U": 3,
            "O": 4
            }

id2label = {0: "B",
            1: "I",
            2: "L",
            3: "U",
            4: "O"
            }


class BertForValueExtraction(torch.nn.Module):
    def __init__(self, num_labels=len(id2label.keys()), from_pretrained='bert-base-uncased'):
        super(BertForValueExtraction, self).__init__()
        print(f"Loading BertForTokenClassification as {from_pretrained}")
        self.token_classifier = BertForTokenClassification.from_pretrained(from_pretrained,
                                                                           num_labels=num_labels,
                                                                           return_dict=True)

    def forward(self, input_ids, attention_mask, token_type_ids, labels=None):
        return self.token_classifier(input_ids=input_ids,
                                     attention_mask=attention_mask,
                                     token_type_ids=token_type_ids,
                                     labels=labels)

    def calculate_loss(self, input_ids, attention_mask, token_type_ids, labels):
        outputs = self.forward(input_ids=input_ids,
                               attention_mask=attention_mask,
                               token_type_ids=token_type_ids,
                               labels=labels)
        return outputs.loss

    def predict(self, input_ids, attention_mask=None, token_type_ids=None):
        outputs = self.forward(input_ids=input_ids,
                               attention_mask=attention_mask,
                               token_type_ids=token_type_ids
                               )

        logits = outputs.logits
        preds = torch.max(logits, dim=2)[1]
        return preds

    def evaluate(self, dataloader, device):
        with torch.no_grad():
            TP, FP, FN, TN = 0, 0, 0, 0
            for batch in tqdm(dataloader):
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                token_type_ids = batch['token_type_ids'].to(device)
                labels = batch['labels'].to(device)
                text = batch['text']

                preds = self.predict(input_ids=input_ids,
                                     attention_mask=attention_mask,
                                     token_type_ids=token_type_ids)

                tp, fp, fn, tn = self.evaluate_batch(preds.tolist(), labels.tolist(), attention_mask.tolist())
                TP += tp
                FP += fp
                FN += fn
                TN += tn

        return TP, FP, FN, TN

    def evaluate_batch(self, preds, labels, attention_mask):
        TP, FP, FN, TN = 0, 0, 0, 0
        for pred, label, mask in zip(preds, labels, attention_mask):
            for p, l, m in zip(pred, label, mask):
                if m == 1:
                    if id2label[l] != "O":
                        if p == l:
                            TP += 1
                        else:
                            FN += 1
                    else:
                        if p == l:
                            TN += 1
                        else:
                            FP += 1
        return TP, FP, FN, TN

    def save_(self, model_path):
        self.token_classifier.save_pretrained(model_path)
        print(f"Saving model at {model_path}")

    def predict_sentence_values(self, tokenizer, sentence, device='cuda'):
        if device == 'cuda':
            input_ids = tokenizer(sentence, return_tensors="pt")['input_ids'].to('cuda')
            preds = self.predict(input_ids).cpu().numpy()[0]
            input_ids = input_ids.cpu().numpy()[0]

        if device == 'cpu':
            input_ids = tokenizer(sentence, return_tensors="pt")['input_ids']
            preds = self.predict(input_ids).numpy()[0]
            input_ids = input_ids.numpy()[0]

        values = []
        current_value_tokens = []
        for t, p in zip(input_ids, preds):
            if id2label[p] == "O" and current_value_tokens:
                values.append(tokenizer.decode(current_value_tokens))
                current_value_tokens = []
            if id2label[p] == "B":
                if current_value_tokens:
                    values.append(tokenizer.decode(current_value_tokens))
                current_value_tokens = [t]
            if id2label[p] == "I":
                current_value_tokens.append(t)
        if current_value_tokens:
            values.append(tokenizer.decode(current_value_tokens))
        return values
