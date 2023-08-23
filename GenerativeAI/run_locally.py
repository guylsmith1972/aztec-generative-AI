import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers


class LocalAI:
    def __init__(self):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.MODEL = 'tiiuae/falcon-7b-instruct'


        self.tokenizer = AutoTokenizer.from_pretrained('models/' + self.MODEL)
        self.pipeline = transformers.pipeline(
            "text-generation",
            model=self.MODEL,
            tokenizer=self.tokenizer,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
            device_map="auto",
        )

    def generate_text(self, preamble, query):
        print("Submitting query")

        sequences = self.pipeline(
            preamble + ' ' + query,
            max_length=200,
            do_sample=True,
            top_k=10,
            num_return_sequences=1,
            eos_token_id=self.tokenizer.eos_token_id,
        )
        for seq in sequences:
            print(f"Result: {seq['generated_text']}")

        return ''
