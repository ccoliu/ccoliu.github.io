numbers = []
for i in range(1, 6):
    numbers.append(i)

for i in range(6, 11):
    numbers.append(i)

combined_output = ' '.join(map(str, numbers))
print(combined_output)
