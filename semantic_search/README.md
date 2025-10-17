# Semantic Search Implementation

## 🎯 Overview

This implementation provides a dedicated semantic search system for the Rig Veda Explorer, separate from the ChatBot API. It uses sentence transformers and FAISS for fast, accurate semantic similarity search.

## 🚀 Quick Start

### Backend Setup

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Run Setup Script** (optional):
   ```bash
   # Linux/Mac
   bash setup_semantic_search.sh
   
   # Windows
   setup_semantic_search.bat
   ```

3. **Start the Server**:
   ```bash
   python app.py
   ```

### Frontend Integration

The frontend `SemanticSearch.js` component has been updated to use the new dedicated endpoints instead of the ChatBot API.

## 📡 API Endpoints

### `POST /api/semantic/search`
**Search for verses by semantic similarity**

**Request Body**:
```json
{
  "query": "fire and sacrifice",
  "top_k": 10
}
```

**Response**:
```json
{
  "query": "fire and sacrifice",
  "results": [
    {
      "location": "01.001.01",
      "sanskrit": "अग्निमीळे पुरोहितं...",
      "translation": "I praise Agni, the chosen Priest...",
      "similarity_score": 0.85
    }
  ],
  "total_results": 10,
  "success": true
}
```

### `GET /api/semantic/random`
**Get random verses for exploration**

**Response**:
```json
{
  "results": [...],
  "total_results": 10,
  "success": true
}
```

### `GET /api/semantic/status`
**Check if semantic search is ready**

**Response**:
```json
{
  "ready": true,
  "model_loaded": true,
  "index_loaded": true,
  "data_loaded": true,
  "total_verses": 10552
}
```

## 🔧 Technical Architecture

### Components

1. **SentenceTransformer Model**: `all-MiniLM-L6-v2` for encoding queries
2. **FAISS Index**: Fast similarity search with inner product (cosine similarity)
3. **Data Pipeline**: Loads verses from mandala JSON files
4. **Embedding Pipeline**: Uses pre-computed embeddings or builds index on startup

### File Structure

```
backend/
├── semantic_search/
│   ├── __init__.py
│   └── routes.py          # Main semantic search logic
├── data/
│   ├── embeddings/        # Pre-computed embeddings
│   │   ├── mandala_1_embeddings.json
│   │   ├── ...
│   │   └── FAISS_index    # Built automatically
│   └── dataset/           # Verse data
│       ├── mandala_1.json
│       └── ...
└── app.py                 # Updated with semantic_search_bp
```

## 🎯 Key Features

### Backend Features
- **Fast Similarity Search**: FAISS-powered vector search
- **Automatic Index Building**: Creates FAISS index from embeddings if missing
- **Memory Efficient**: Loads components once at startup
- **Error Handling**: Graceful fallbacks and informative error messages
- **Flexible Results**: Configurable number of results

### Frontend Features
- **Dedicated API**: No longer uses ChatBot API for semantic search
- **Enhanced UX**: Better loading states and error handling
- **Random Exploration**: "Surprise Me" uses dedicated random endpoint
- **Consistent Format**: Results transformed to match existing SearchResults component

## 🔄 Migration from ChatBot API

### What Changed

**Before**: SemanticSearch → ChatBot API → LLM processing → Results
**After**: SemanticSearch → Dedicated Semantic API → Direct Results

### Benefits

1. **Performance**: Direct vector search without LLM overhead
2. **Reliability**: No dependency on external LLM services
3. **Speed**: Faster response times for search queries
4. **Scalability**: Can handle more concurrent searches
5. **Customization**: Full control over search algorithm and ranking

### Backward Compatibility

The frontend transformation ensures that results still work with the existing `SearchResults` component by maintaining the expected data structure.

## 🛠️ Configuration

### Environment Variables
- No additional environment variables required
- Uses existing Flask configuration

### Performance Tuning
- **FAISS Index Type**: Currently uses `IndexFlatIP` (exact search)
- **Model**: `all-MiniLM-L6-v2` (balance of speed and accuracy)
- **Top-K Results**: Configurable per request (default: 10)

## 🔍 Usage Examples

### Simple Theme Search
```javascript
// Frontend
const response = await fetch('/api/semantic/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: "fire and sacrifice" })
});
```

### Advanced Search with More Results
```javascript
const response = await fetch('/api/semantic/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    query: "cosmic creation and divine order",
    top_k: 20
  })
});
```

### Random Exploration
```javascript
const response = await fetch('/api/semantic/random');
```

## 🐛 Troubleshooting

### Common Issues

1. **"Search components not properly loaded"**
   - Ensure embeddings files exist in `data/embeddings/`
   - Check that dataset files exist in `data/dataset/`

2. **"FAISS index not found"**
   - Index will be built automatically from embeddings
   - Ensure embedding files are properly formatted

3. **"No embeddings found to build FAISS index"**
   - Generate embeddings first using your embedding script
   - Ensure embedding files contain valid embedding arrays

4. **Slow first request**
   - Model and index loading happens on first request if not pre-loaded
   - Subsequent requests will be fast

### Performance Tips

1. **Pre-build FAISS Index**: Run the server once to build and save the FAISS index
2. **Memory**: Ensure sufficient RAM for loading all embeddings (~500MB-1GB)
3. **CPU**: SentenceTransformer model benefits from multiple CPU cores

## 🚀 Future Enhancements

- [ ] GPU acceleration for larger models
- [ ] Approximate search with IVF index for massive datasets
- [ ] Caching layer for frequent queries
- [ ] Advanced filtering by mandala, hymn, or metadata
- [ ] Query expansion and synonym handling
- [ ] Multi-language search support