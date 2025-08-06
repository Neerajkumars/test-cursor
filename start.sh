#!/bin/bash

# Dynamic API Microservice Startup Script

echo "🚀 Starting Dynamic API Microservice"
echo "===================================="

# Check if Docker Compose is available
if command -v docker-compose &> /dev/null; then
    echo "📦 Using Docker Compose..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        echo "📝 Creating .env file from template..."
        cp .env.example .env
    fi
    
    # Start services
    echo "🔄 Starting PostgreSQL and API service..."
    docker-compose up -d
    
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        echo "✅ Services started successfully!"
        echo ""
        echo "🌐 Service URLs:"
        echo "   • API Documentation: http://localhost:8000/docs"
        echo "   • ReDoc: http://localhost:8000/redoc"
        echo "   • Health Check: http://localhost:8000/health"
        echo "   • Management API: http://localhost:8000/manage/apis"
        echo ""
        echo "🧪 To test the service, run:"
        echo "   python3 test_api.py"
        echo ""
        echo "🛑 To stop the services:"
        echo "   docker-compose down"
    else
        echo "❌ Failed to start services. Check Docker logs:"
        echo "   docker-compose logs"
    fi
    
elif command -v python3 &> /dev/null; then
    echo "🐍 Using local Python installation..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo "🔄 Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        echo "📝 Creating .env file from template..."
        cp .env.example .env
        echo "⚠️  Please configure your PostgreSQL connection in .env"
    fi
    
    # Start the application
    echo "🚀 Starting the application..."
    echo "⚠️  Make sure PostgreSQL is running and configured in .env"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    
else
    echo "❌ Neither Docker Compose nor Python 3 found."
    echo "   Please install Docker Compose or Python 3 to run this service."
    exit 1
fi