import torch
from elasticsearch import Elasticsearch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from datasets import Dataset
from peft import LoraConfig, get_peft_model
import os

# ✅ Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200")

# ✅ Fetch historical logs & resolutions
def fetch_logs_from_es():
    query = {"query": {"match_all": {}}}
    response = es.search(index="logs_index", body=query, size=1000)  # Load max logs
    logs = []
    resolutions = []
    for hit in response["hits"]["hits"]:
        logs.append(hit["_source"]["log_text"])
        resolutions.append(hit["_source"]["resolution"])
    return logs, resolutions

logs, resolutions = fetch_logs_from_es()

# ✅ Prepare dataset for training
dataset = Dataset.from_dict({"log_text": logs, "resolution": resolutions})

# ✅ Load model & tokenizer (Mistral 7B or Llama 3)
model_name = "mistralai/Mistral-7B-Instruct"  # Change if using another model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")

# ✅ Apply LoRA for fine-tuning (optional, improves efficiency)
lora_config = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05)
model = get_peft_model(model, lora_config)

# ✅ Tokenize dataset
def tokenize_function(examples):
    return tokenizer(
        [f"Log: {log}\nResolution: {res}" for log, res in zip(examples["log_text"], examples["resolution"])],
        truncation=True,
        padding="max_length",
        max_length=512
    )

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# ✅ Define training arguments
training_args = TrainingArguments(
    output_dir="./trained_model",
    per_device_train_batch_size=2,
    num_train_epochs=3,
    save_strategy="epoch",
    logging_steps=10,
    evaluation_strategy="epoch",
    report_to="none",
    load_best_model_at_end=True
)

# ✅ Train the model
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset
)
trainer.train()

# ✅ Save model & tokenizer
save_path = "./log_analysis_model"
model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)
print(f"✅ Model saved at {save_path}")
