import nltk
nltk.download('gutenberg')
import hashlib
from nltk.corpus import gutenberg
from typing import Set, List, Dict

# The next instruction downloads the corpus
# ATTENTION!!! Run this instruction once only for each Python installation,
# then comment it!!

#nltk.download("gutenberg")  

shingle_size = 3  # The character length of each shingle

b = 4  # The number of bands for LSH
r = 3  # The number of rows per band for LSH
num_hash_functions = b * r	# The number of the minhash functions

# The size of the prefix of each document to be loaded
DOCLENGTH = 3000

# Extracts and returns as a set all shingles of size shingle_size from document doc
def extract_shingles(doc : str, shingle_size : int):
    shingles = set()			# initially shingles is an empty set
    for i in range(len(doc) - shingle_size + 1): # Iterate over entire document, one character at a time and
        shingle = doc[i:i + shingle_size]	#    extract shingle from current character 
        shingles.add(shingle)   # Since shingles is a set, if a shingle
                                # is already in it, it is not added again
    return shingles

# Computes and returns the Jaccard similarity 
# between two sets of shingles, s1 and s2
def jaccard_similarity(s1: Set[str], s2: Set[str]):
    intersection = s1.intersection(s2)
    union = s1.union(s2)
    return len(intersection) / len(union)

# Computes and returns a signature for a set of shingles,
# with num_hash_functions hash functions
def minhash_signature(shingles : Set[str], num_hash_functions : int):
    signature = []		# Initially signature is an empty list
    for i in range(num_hash_functions):
        min_hash = float('inf')
        for shingle in shingles:
                # The next instriction creates a hash value that depends on 'shingle', 
                # concatenated with the number of the hash function as a string.
                # In this way we create easily multiple hash functions (one for each 
                # hash function id), not by changing the hash function
                # (which is always the md5),  but by changing the strings to be hashed. 
                # hexdigest() method returns the hash value as a string (instead of
                # a hash object) in hexadecimal format, whereas int(…, 16) 
                # converts this string to an integer.
                # Note that the number of possible hash values returned by md5() is extra large,
                # so we take the module of the returned value to a smaller value, e.g. 10000. 
				# However, the code works even without taking the modulo.
                # Note finally that hashlib.md5() (as well as other hash functions from 
                # hashlib) takes as input byte strings only, thus the need for “encode()”.
            hash_value = int(hashlib.md5((str(i) + shingle).encode()).hexdigest(), 16) % 10000
            min_hash = float('inf')  # Start with infinity for each hash function
            for shingle in shingles:  # Iterate through each shingle
            # Compute the hash value using hashlib
              hash_value = int(hashlib.md5((str(i) + shingle).encode()).hexdigest(), 16) % 10000
            min_hash = min(min_hash, hash_value)  # Update the minimum hash value
        signature.append(min_hash)  # Add min_hash to the signature list
  # You have to add min_hash at the end of list signature
    return signature

# This function distributes the signatures in buckets
def lsh(signatures : List[List[int]], b : int, r : int):
    # buckets are defined as a dictionary. The keys in the dictionary are the bucket numbers (integers)
	# In this implementation the set buckets is shared by all bands
    buckets = {}
    for doc_num, signature in enumerate(signatures):
        # doc_num takes increasing integer values, starting from 0
		# signature takes the values in signatures
        for band_num in range(b):
			# band is assigned a sublist of the signature, with r only numbers
            band = tuple(signature[band_num * r:(band_num + 1) * r])
            	# hash() method returns a hash value for any python object. 
                # Compared to hashlib.md5() it has two differences:
                # i) It gets as input any immutable object, instead of byte strings
                # ii) It is randomized at the start of the python session, 
                # so identical objects during different python sessions get different
                # hash values.
                # hash() computes a hash value for the part of the signature in the band.
                # Note that hash() function returns a huge number of possible hash 
                # values, thus for two bands to be hashed in the same bucket they
                # have to be identical, except if we take the modulo to some smaller value.
            hash_value = hash(band) % 10000
            if hash_value in buckets: 	# there is already another document
                                        # in the same bucket (possibly by another band)
                buckets[hash_value].add(doc_num)
            else:
                buckets[hash_value] = {doc_num}   	# this is the first 
                                                    # document in the particular bucket
    return buckets

# Returns all pairs of documents that co-appear in some bucket
def find_candidate_pairs(buckets : Dict[int, Set[int]]):
    candidate_pairs = set()		# initially an empty set
    for bucket in buckets.values():
        if len(bucket) > 1:
            for doc1 in bucket:
                for doc2 in bucket:
                    if doc1 < doc2:
                        candidate_pairs.add((doc1, doc2))
    return candidate_pairs

# Load three document from each one of three authors (nine documents totally) 
docs = [
    # Reading the first DOCLENGTH chars of each document
    gutenberg.raw("austen-emma.txt")[:DOCLENGTH],  
    gutenberg.raw("austen-persuasion.txt")[:DOCLENGTH],  
    gutenberg.raw("austen-sense.txt")[:DOCLENGTH], 
    gutenberg.raw("chesterton-ball.txt")[:DOCLENGTH], 
    gutenberg.raw("chesterton-brown.txt")[:DOCLENGTH], 
    gutenberg.raw("chesterton-thursday.txt")[:DOCLENGTH], 
    gutenberg.raw("shakespeare-caesar.txt")[:DOCLENGTH], 
    gutenberg.raw("shakespeare-hamlet.txt")[:DOCLENGTH], 
    gutenberg.raw("shakespeare-macbeth.txt")[:DOCLENGTH] ]

# Extract the set of shingles for each document
shingle_sets = [extract_shingles(doc, shingle_size) for doc in docs]

# Compute Jaccard similarity between all pairs of documents
print("Jaccard Similarities:")
for i in range(len(docs)):
    for j in range(i + 1, len(docs)):
        similarity = jaccard_similarity(shingle_sets[i], shingle_sets[j])
        print(f"Document {i} and Document {j}: {similarity:.3f}")

# Compute minhash signatures for each document
signatures = [minhash_signature(shingles, num_hash_functions) for shingles in shingle_sets]

# Distribute signatures to buckets using lsh
buckets = lsh(signatures, b, r)

# Find candidate pairs from buckets
candidate_pairs = find_candidate_pairs(buckets)
print("\nCandidate Pairs (from LSH):")
for pair in candidate_pairs:
    print(f"Document {pair[0]} and Document {pair[1]}")
	
