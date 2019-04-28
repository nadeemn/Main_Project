import gensim.models.keyedvectors as word2vec

models = word2vec.KeyedVectors.load_word2vec_format(
        'C:/Users/Nadeem/PycharmProjects/I-recruit/GoogleNews-vectors-negative300.bin', binary=True)

print("model successfully loaded")
