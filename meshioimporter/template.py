def preprocess(fileseq,frame_number):
    frame_number = frame_number % len(fileseq)
    mesh = meshio.read(fileseq[frame_number])
    return mesh
