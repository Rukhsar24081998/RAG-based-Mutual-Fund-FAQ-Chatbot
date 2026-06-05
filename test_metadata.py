from ingest.chunker import parse_metadata_from_file

with open('data/extracted/custom_facts.txt', 'r', encoding='utf-8') as f:
    text = f.read()

metadata = parse_metadata_from_file(text)
print(f"Metadata: {metadata}")

content = text.split("="*80)[-1].strip()
print(f"\nContent preview: {content[:200]}...")
