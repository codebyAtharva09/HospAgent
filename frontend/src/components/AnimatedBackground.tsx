import { useEffect, useRef } from "react";

export const AnimatedBackground = () => {
    const videoRef = useRef<HTMLVideoElement>(null);

    useEffect(() => {
        if (videoRef.current) {
            videoRef.current.playbackRate = 0.7; // Slow down slightly for a more premium feel
        }
    }, []);

    return (
        <div className="fixed inset-0 -z-20 overflow-hidden bg-slate-950">
            {/* 
                Video Source: Abstract Medical/Tech Background
                You can replace this URL with any local video file in your public folder 
                e.g., src="/videos/medical-bg.mp4"
            */}
            <video
                ref={videoRef}
                autoPlay
                loop
                muted
                playsInline
                className="absolute min-w-full min-h-full object-cover opacity-60"
            >
                <source
                    src="https://cdn.pixabay.com/video/2020/04/17/36337-413763472_large.mp4"
                    type="video/mp4"
                />
                Your browser does not support the video tag.
            </video>

            {/* Gradient Overlay to ensure text readability */}
            <div className="absolute inset-0 bg-gradient-to-b from-white/80 via-white/50 to-white/80 dark:from-slate-950/80 dark:via-slate-950/60 dark:to-slate-950/90 backdrop-blur-[2px]" />

            {/* Blue tint overlay for medical theme consistency */}
            <div className="absolute inset-0 bg-blue-500/10 mix-blend-overlay" />
        </div>
    );
};

