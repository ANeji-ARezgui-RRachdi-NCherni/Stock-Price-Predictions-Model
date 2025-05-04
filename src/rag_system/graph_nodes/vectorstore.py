

# def process_pdf(file_path):
#     """
#     Load data from a PDF file.
    
#     Args:
#         file_path (str): Path to the PDF file.
    
#     Returns:
#         list: Loaded data as a list of IDs.
#     """
#     md = MarkItDown()
#     result = md.convert(file_path)
#     chunker = SemanticChunker(
#             embedding_model=doc_embeddings,
#             threshold=0.5,
#             chunk_size=512,
#             min_sentences=1
#         )
#     chunks = chunker.chunk(result.text_content)
#     all_splits = [Document(page_content=chunk.text) for chunk in chunks]
#     try:
#         ids = vector_store.add_documents(all_splits)
#     except Exception as e:
#         print(f"Error adding documents: {e}")  
#         ids = []
#     return ids      
    






    


    