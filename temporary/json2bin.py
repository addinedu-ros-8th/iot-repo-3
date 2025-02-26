# Example integer
x = 12345

# Convert to a 4-byte binary representation in big-endian order
binary_data = x.to_bytes(4, byteorder='big', signed=True)

print(binary_data)  # Output will be a bytes object
