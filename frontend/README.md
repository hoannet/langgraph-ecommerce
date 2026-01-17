# LangGraph Chat Frontend

A modern TypeScript/React frontend for the LangGraph chatbot with integrated payment processing.

## Features

- 🤖 **AI Chat Interface**: Real-time conversation with LangGraph backend
- 💳 **Payment Processing**: Natural language payment requests through chat
- 🎨 **Modern UI**: Dark theme with glassmorphism effects
- 📱 **Responsive Design**: Works on desktop and mobile
- 🔄 **Session Management**: Persistent chat sessions
- 🎯 **Intent Classification**: Visual indicators for detected intents

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Zustand** - State management
- **Axios** - HTTP client

## Getting Started

### Prerequisites

- Node.js 16+ (Note: There may be compatibility issues with Node.js 24+)
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
npm run preview
```

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── ChatContainer.tsx
│   │   ├── MessageList.tsx
│   │   ├── MessageInput.tsx
│   │   ├── IntentBadge.tsx
│   │   └── PaymentCard.tsx
│   ├── services/         # API services
│   │   ├── api.ts
│   │   ├── chatService.ts
│   │   └── paymentService.ts
│   ├── store/           # State management
│   │   └── chatStore.ts
│   ├── types/           # TypeScript types
│   │   ├── api.ts
│   │   └── chat.ts
│   ├── App.tsx          # Main app component
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Usage

### Sending Messages

Simply type your message in the input field and press Enter or click the send button.

### Payment Processing

To process a payment, send a natural language message like:
- "I want to pay $50"
- "Process payment of 100 USD"
- "Charge me $25.99"

The backend will detect the payment intent and process it accordingly.

### Clearing History

Click the "Clear History" button in the header to clear the current session's chat history.

## API Integration

The frontend connects to the following backend endpoints:

- `POST /chat/` - Send chat messages
- `GET /chat/{session_id}/history` - Get chat history
- `POST /chat/{session_id}/clear` - Clear chat history
- `POST /payment/process` - Process payments
- `GET /payment/{transaction_id}` - Get transaction status

## Customization

### Changing Colors

Edit CSS variables in `src/index.css`:

```css
:root {
  --accent-primary: #667eea;
  --accent-secondary: #764ba2;
  /* ... more variables */
}
```

### Backend URL

Update the API base URL in `.env` or `src/services/api.ts`

## Troubleshooting

### Node.js Compatibility

If you encounter issues with Node.js 24+, try using Node.js 18 or 20:

```bash
nvm install 18
nvm use 18
npm install
```

### CORS Issues

Ensure the backend has CORS enabled for `http://localhost:3000`

### Connection Refused

Make sure the backend is running on the configured URL (default: `http://localhost:8000`)
