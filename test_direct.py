from rag.assembler import generate_answer

print("="*50)
print("Test 1: Capital gains statement")
result = generate_answer("How to download my capital gains statement?")
print(result['answer'])

print("\n" + "="*50)
print("Test 2: Login")
result = generate_answer("How do I log in to my account?")
print(result['answer'])

print("\n" + "="*50)
print("Test 3: Expense ratio (no links)")
result = generate_answer("What is the expense ratio for HDFC Flexi Cap Fund?")
print(result['answer'])
