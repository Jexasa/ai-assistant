from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def prepare_data():
    conn = sqlite3.connect("feedback.db")
    cursor = conn.execute("SELECT task, response, feedback FROM feedback")
    data = [{"prompt": row[0], "response": row[1], "feedback": row[2]} for row in cursor.fetchall()]
    conn.close()
    return {"train": data}

def fine_tune():
    model_name = "google/gemma-2-9b"
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    dataset = load_dataset("json", data_files=prepare_data())
    
    def tokenize_function(examples):
        return tokenizer(examples["prompt"] + " " + examples["feedback"], truncation=True, max_length=512)
    
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    
    training_args = TrainingArguments(
        output_dir="./fine_tuned_model",
        num_train_epochs=3,
        per_device_train_batch_size=1,
        save_steps=500,
        save_total_limit=2,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
    )
    
    logger.info("Starting fine-tuning")
    trainer.train()
    model.save_pretrained("./fine_tuned_model")
    tokenizer.save_pretrained("./fine_tuned_model")
    logger.info("Fine-tuning complete")

if __name__ == "__main__":
    fine_tune()