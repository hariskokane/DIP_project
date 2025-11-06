# Defect Detection Frontend

Modern React TypeScript frontend for the Defect Detection System.

## Features

- **Live View**: Real-time display of current bottle inspection
- **Dashboard**: Analytics and statistics with interactive charts
- **History**: Searchable and filterable inspection history
- **Modern UI**: Built with TailwindCSS and Lucide icons

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## API Configuration

The frontend expects the API server to be running at `http://localhost:8000`. This is configured in `vite.config.ts` as a proxy.
