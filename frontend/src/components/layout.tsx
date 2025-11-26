import { Link } from "react-router-dom";
import { ModeToggle } from "./mode-toggle";
import { Activity, LayoutDashboard, Home as HomeIcon, Sparkles } from "lucide-react";
import { AnimatedBackground } from "./AnimatedBackground";

export const Layout = ({ children }: { children: React.ReactNode }) => {
    return (
        <div className="min-h-screen bg-background font-sans antialiased transition-colors duration-300">
            <AnimatedBackground />
            {/* Glassmorphism Navbar */}
            <nav className="fixed top-0 z-50 w-full border-b border-white/10 bg-white/5 backdrop-blur-xl supports-[backdrop-filter]:bg-white/5">
                <div className="container flex h-16 items-center justify-between px-4">
                    <div className="flex items-center gap-2">
                        <Link to="/" className="flex items-center gap-2 transition-opacity hover:opacity-80">
                            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg shadow-blue-500/20">
                                <Activity className="h-5 w-5 text-white" />
                            </div>
                            <span className="hidden text-lg font-bold tracking-tight sm:inline-block bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent dark:from-blue-400 dark:to-purple-400">
                                HospAgent
                            </span>
                        </Link>

                        <div className="ml-8 hidden md:flex gap-6">
                            <Link to="/" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors flex items-center gap-1">
                                <HomeIcon className="h-4 w-4" /> Home
                            </Link>
                            <Link to="/dashboard" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors flex items-center gap-1">
                                <LayoutDashboard className="h-4 w-4" /> Dashboard
                            </Link>
                            <Link to="/agentic-showcase" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors flex items-center gap-1">
                                <Sparkles className="h-4 w-4" /> AI Showcase
                            </Link>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <ModeToggle />
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="pt-16 min-h-screen bg-gradient-to-br from-slate-50 via-slate-100 to-slate-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
                {children}
            </main>
        </div>
    );
};
