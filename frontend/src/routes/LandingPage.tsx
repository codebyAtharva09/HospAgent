import React from 'react';
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Activity, ShieldCheck, Zap, BarChart3 } from "lucide-react";
import { Button } from "../components/ui/button";

export const LandingPage = () => {
    return (
        <div className="relative overflow-hidden bg-white dark:bg-slate-950 min-h-screen">
            {/* Hero Section */}
            <section className="relative pt-20 pb-32 md:pt-32 md:pb-48 overflow-hidden">
                <div className="absolute inset-0 z-0 w-full h-full overflow-hidden">
                    <video
                        autoPlay
                        loop
                        muted
                        playsInline
                        className="absolute inset-0 w-full h-full object-cover blur-[1.4px] opacity-60"
                    >
                        <source src="/Pulse_Rate_Wave_Video_Generated.mp4" type="video/mp4" />
                        Your browser does not support the video tag.
                    </video>
                    {/* Overlay to ensure text contrast if video is too bright/busy */}
                    <div className="absolute inset-0 bg-white/30 dark:bg-black/40 backdrop-blur-[2px]"></div>
                </div>

                <div className="container px-4 mx-auto text-center relative z-10">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                    >
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 text-blue-600 dark:text-blue-400 text-sm font-medium mb-6 border border-blue-500/20 backdrop-blur-sm">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                            </span>
                            Live Hospital Intelligence
                        </div>

                        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 bg-gradient-to-r from-gray-900 via-blue-800 to-gray-900 dark:from-white dark:via-blue-200 dark:to-white bg-clip-text text-transparent drop-shadow-sm">
                            Next-Gen AI for <br className="hidden md:block" />
                            <span className="text-blue-600 dark:text-blue-400">Smarter Healthcare</span>
                        </h1>

                        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
                            Optimize staffing, predict patient flow, and manage inventory with our
                            autonomous agentic system. Real-time insights for modern hospitals.
                        </p>

                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                            <Link to="/dashboard/overview">
                                <Button size="lg" className="h-12 px-8 rounded-full text-lg bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 transition-all duration-300 hover:-translate-y-1">
                                    Launch Dashboard <ArrowRight className="ml-2 h-5 w-5" />
                                </Button>
                            </Link>
                            <Button variant="outline" size="lg" className="h-12 px-8 rounded-full text-lg border-2 hover:bg-accent/50 backdrop-blur-sm">
                                View Documentation
                            </Button>
                        </div>
                    </motion.div>
                </div>

                {/* Floating Elements Animation */}
                <div className="absolute top-1/2 left-10 -z-10 opacity-30 dark:opacity-20 hidden lg:block">
                    <motion.div
                        animate={{ y: [0, -20, 0], rotate: [0, 5, 0] }}
                        transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
                        className="w-64 h-64 rounded-3xl bg-gradient-to-br from-purple-500/30 to-blue-500/30 blur-3xl"
                    />
                </div>
                <div className="absolute bottom-0 right-10 -z-10 opacity-30 dark:opacity-20 hidden lg:block">
                    <motion.div
                        animate={{ y: [0, 30, 0], rotate: [0, -5, 0] }}
                        transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
                        className="w-72 h-72 rounded-full bg-gradient-to-tr from-blue-500/30 to-teal-500/30 blur-3xl"
                    />
                </div>
            </section>

            {/* Features Grid */}
            <section className="pt-20 pb-24 bg-white/50 dark:bg-slate-950/50 backdrop-blur-sm border-t border-white/10">
                <div className="container px-4 mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.5 }}
                        className="text-center mb-16"
                    >
                        <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-gray-900 to-blue-800 dark:from-white dark:to-blue-200 bg-clip-text text-transparent">
                            Core Features
                        </h2>
                        <div className="h-1 w-20 bg-blue-500 mx-auto rounded-full"></div>
                    </motion.div>
                    <div className="grid md:grid-cols-3 gap-8">
                        {[
                            {
                                icon: <BarChart3 className="h-8 w-8 text-blue-500" />,
                                title: "Predictive Analytics",
                                desc: "Forecast patient inflow and resource demand with 95% accuracy using advanced ML models."
                            },
                            {
                                icon: <Zap className="h-8 w-8 text-amber-500" />,
                                title: "Real-time Optimization",
                                desc: "Autonomous agents adjust staffing and inventory levels instantly based on live data."
                            },
                            {
                                icon: <ShieldCheck className="h-8 w-8 text-emerald-500" />,
                                title: "Proactive Advisory",
                                desc: "Generate health advisories and risk assessments automatically before crises occur."
                            }
                        ].map((feature, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.1 }}
                                viewport={{ once: true }}
                                className="group p-8 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-lg shadow-blue-500/20 dark:shadow-blue-900/30 hover:shadow-2xl hover:shadow-blue-500/40 transition-all duration-300 hover:-translate-y-1"
                            >
                                <div className="mb-6 p-4 rounded-2xl bg-slate-50 dark:bg-slate-800 w-fit group-hover:scale-110 transition-transform duration-300">
                                    {feature.icon}
                                </div>
                                <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                                <p className="text-muted-foreground leading-relaxed">
                                    {feature.desc}
                                </p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>
        </div>
    );
};
