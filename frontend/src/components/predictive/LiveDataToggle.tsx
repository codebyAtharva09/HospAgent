import React from 'react';

interface LiveDataToggleProps {
    liveMode: boolean;
    setLiveMode: (mode: boolean) => void;
}

const LiveDataToggle: React.FC<LiveDataToggleProps> = ({ liveMode, setLiveMode }) => {
    return (
        <label className="flex items-center space-x-3 cursor-pointer select-none">
            <span className="text-sm font-semibold text-slate-700">Live Data Mode</span>
            <div
                className={`w-12 h-6 flex items-center rounded-full p-1 duration-300 transition-colors ${liveMode ? "bg-green-500" : "bg-gray-300"
                    }`}
                onClick={(e) => {
                    e.preventDefault();
                    setLiveMode(!liveMode);
                }}
            >
                <div
                    className={`bg-white w-4 h-4 rounded-full shadow-md transform duration-300 transition-transform ${liveMode ? "translate-x-6" : "translate-x-0"
                        }`}
                ></div>
            </div>
        </label>
    );
};

export default LiveDataToggle;
