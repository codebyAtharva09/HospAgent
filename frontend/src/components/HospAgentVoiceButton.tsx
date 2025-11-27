import React, { useState, useEffect } from 'react';
import Vapi from '@vapi-ai/web';
import { Mic, MicOff, Loader2 } from 'lucide-react';

// Initialize Vapi client
// Ensure you have VITE_VAPI_PUBLIC_KEY in your .env
const vapi = new Vapi(import.meta.env.VITE_VAPI_PUBLIC_KEY || "demo-key");

export const HospAgentVoiceButton = () => {
    const [isSessionActive, setIsSessionActive] = useState(false);
    const [status, setStatus] = useState<'idle' | 'connecting' | 'listening' | 'speaking'>('idle');

    useEffect(() => {
        // Vapi Event Listeners
        const onCallStart = () => {
            setIsSessionActive(true);
            setStatus('listening');
        };

        const onCallEnd = () => {
            setIsSessionActive(false);
            setStatus('idle');
        };

        const onSpeechStart = () => {
            setStatus('listening');
        };

        const onSpeechEnd = () => {
            setStatus('speaking');
        };

        const onError = (e: any) => {
            console.error("Vapi Error:", e);
            setIsSessionActive(false);
            setStatus('idle');
        };

        vapi.on('call-start', onCallStart);
        vapi.on('call-end', onCallEnd);
        vapi.on('speech-start', onSpeechStart);
        vapi.on('speech-end', onSpeechEnd);
        vapi.on('error', onError);

        return () => {
            vapi.off('call-start', onCallStart);
            vapi.off('call-end', onCallEnd);
            vapi.off('speech-start', onSpeechStart);
            vapi.off('speech-end', onSpeechEnd);
            vapi.off('error', onError);
        };
    }, []);

    const toggleCall = async () => {
        if (isSessionActive) {
            vapi.stop();
        } else {
            setStatus('connecting');
            try {
                // Ensure you have VITE_VAPI_ASSISTANT_ID in your .env
                await vapi.start(import.meta.env.VITE_VAPI_ASSISTANT_ID);
            } catch (err) {
                console.error("Failed to start Vapi session:", err);
                setStatus('idle');
            }
        }
    };

    // Visuals based on status
    const getButtonStyles = () => {
        switch (status) {
            case 'connecting':
                return 'bg-yellow-500/20 border-yellow-500 text-yellow-500';
            case 'listening':
                return 'bg-green-500/20 border-green-500 text-green-500 animate-pulse';
            case 'speaking':
                return 'bg-blue-500/20 border-blue-500 text-blue-500';
            case 'idle':
            default:
                return 'bg-slate-800 border-slate-600 text-slate-400 hover:text-white hover:border-slate-400';
        }
    };

    return (
        <button
            onClick={toggleCall}
            className={`
                relative flex items-center gap-3 px-6 py-3 rounded-full border-2 transition-all duration-300
                font-bold tracking-wider uppercase shadow-lg hover:shadow-xl
                ${getButtonStyles()}
            `}
        >
            {/* Animated Ring for Active State */}
            {isSessionActive && (
                <span className="absolute inset-0 rounded-full border-2 border-current opacity-50 animate-ping"></span>
            )}

            {/* Icon */}
            {status === 'connecting' ? (
                <Loader2 className="w-5 h-5 animate-spin" />
            ) : isSessionActive ? (
                <Mic className="w-5 h-5" />
            ) : (
                <MicOff className="w-5 h-5" />
            )}

            {/* Text */}
            <span>
                {status === 'idle' && "Talk to HospAgent"}
                {status === 'connecting' && "Connecting..."}
                {status === 'listening' && "Listening..."}
                {status === 'speaking' && "HospAgent Speaking..."}
            </span>
        </button>
    );
};
