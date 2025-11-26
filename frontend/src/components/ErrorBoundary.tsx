import React, { Component, ReactNode } from 'react';

interface Props {
    children: ReactNode;
    errorInfo?: { endpoint: string; status: number; message: string };
}

interface State {
    hasError: boolean;
    error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: any) {
        console.error('ErrorBoundary caught:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            const { errorInfo } = this.props;
            return (
                <div className="error-boundary-container">
                    <div className="error-boundary-card">
                        <h2>⚠️ Something went wrong</h2>
                        <p className="error-message">
                            The dashboard encountered an unexpected error. This usually happens when:
                        </p>
                        <ul className="error-list">
                            <li>The backend server is not running</li>
                            <li>Live Data Mode received unexpected data</li>
                            <li>A network request failed</li>
                        </ul>
                        <button
                            className="error-reload-btn"
                            onClick={() => window.location.reload()}
                        >
                            Reload Dashboard
                        </button>
                        {errorInfo && (
                            <details className="error-details">
                                <summary>Technical Details</summary>
                                <pre>Endpoint: {errorInfo.endpoint}</pre>
                                <pre>Status: {errorInfo.status}</pre>
                                <pre>Message: {errorInfo.message}</pre>
                                <pre>{this.state.error?.toString()}</pre>
                            </details>
                        )}
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
