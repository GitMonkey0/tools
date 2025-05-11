from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTTrainer, SFTConfig, DataCollatorForCompletionOnlyLM
from datasets import Dataset
import json, yaml

with open("train.json", "r") as f:
    data = json.load(f)

with open("train_sft.yaml", "r") as f:
    config = yaml.safe_load(f)

dataset = Dataset.from_list(data)

split_dataset = dataset.train_test_split(test_size=0.1, seed=42)

train_dataset = split_dataset["train"]
test_dataset = split_dataset["test"]

if __name__ == "__main__":
    model_path = config["model_path"]
    del config["model_path"]
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype="auto",
    )
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    def formatting_func(example):
        messages = [
            {"role": "system", "content": example["instruction"]},
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
        text = {"text": tokenizer.apply_chat_template(messages, tokenize=False)}
        return text

    collator = DataCollatorForCompletionOnlyLM(
        response_template="<|im_start|>assistant\n",
        tokenizer=tokenizer
    )

    train_dataset = train_dataset.map(formatting_func)
    test_dataset = test_dataset.map(formatting_func)

    training_args = SFTConfig(**config)
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        data_collator=collator
    )

    print("开始训练...")
    trainer.train()
