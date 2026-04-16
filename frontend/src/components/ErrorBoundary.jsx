/**
 * Error Boundary para React
 * 
 * Captura errores en cualquier componente hijo y muestra
 * una pantalla de error amigable en vez de romper toda la app.
 */

import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ error, errorInfo });
    console.error('ErrorBoundary capturó un error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center h-screen bg-gradient-to-br from-red-50 to-orange-100">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-lg text-center">
            <div className="text-6xl mb-4">⚠️</div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Algo salió mal
            </h1>
            <p className="text-gray-600 mb-6">
              Ha ocurrido un error inesperado. Intenta recargar la página.
            </p>
            {this.state.error && (
              <details className="text-left mb-4 bg-gray-50 rounded-lg p-4">
                <summary className="cursor-pointer text-sm font-semibold text-gray-700">
                  Detalles del error
                </summary>
                <pre className="mt-2 text-xs text-red-600 whitespace-pre-wrap overflow-auto max-h-48">
                  {this.state.error.toString()}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}
            <button
              onClick={() => window.location.reload()}
              className="bg-amber-600 hover:bg-amber-700 text-white font-bold py-3 px-6 rounded-xl transition-colors"
            >
              🔄 Recargar Aplicación
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
