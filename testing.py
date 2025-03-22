import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import BitsAndBytesConfig
import docx2txt

model_path = "./trained_deepseek_r1_8b"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True
)

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    device_map="auto",
    quantization_config=bnb_config,
)

tokenizer = AutoTokenizer.from_pretrained(model_path)

model.eval()

def deepseekr18b(transcript):

    transcript = docx2txt.process(transcript)

    prompt = (
        "Organize the transcript into structured meeting minutes:\n"
        "1. Opening Information: Include the date of the meeting, start time, and end time.\n"
        "2. Present Members: List all attendees. If a person is designated as host, add '(Host)' next to their name.\n"
        "3. Absent Members: List any members not present.\n"
        "4. Agenda Approval: Mention if the agenda was reviewed/approved.\n"
        "5. Previous Meeting Minutes Approval: Confirm if last meeting's minutes were approved.\n"
        "6. Summary of Last Meeting Notes and Decisions: Briefly summarize the previous meeting's key points.\n"
        "7. Detailed Summary and Key Points of the Current Meeting: Summarize discussions, action items, and key takeaways.\n"
        "8. Adjournment Time: State the meeting's end time.\n\n"
        f"Transcript:\n{transcript}"
    )

    # this tokenizes the transcript
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=2048,
        padding="max_length"
    ).to("cuda")

    # generates the summary
    with torch.no_grad():
        output_tokens = model.generate(
            **inputs,
            max_new_tokens=1024,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
            num_return_sequences=1
        )

    # result is decoded and returned
    return tokenizer.decode(output_tokens[0], skip_special_tokens=True)