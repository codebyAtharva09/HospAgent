import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useState } from "react";
import { AlertTriangle, Zap, TrendingUp, Users, Package, MessageSquare, Play, RotateCcw } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import api from "@/services/api";

interface CrisisScenario {
    id: string;
    name: string;
    description: string;
    icon: any;
    color: string;
    triggers: {
        aqi?: number;
        festival?: string;
        epidemic?: string;
        temperature?: number;
    };
}

interface SimulationStep {
    id: number;
    agent: string;
    action: string;
    result: string;
    timestamp: number;
    icon: any;
    color: string;
}

const scenarios: CrisisScenario[] = [
    {
        id: 'diwali_pollution',
        name: 'Diwali + Critical Pollution',
        description: 'AQI 350 + Festival crowds + Firecracker injuries',
        icon: AlertTriangle,
        color: 'rose',
        triggers: { aqi: 350, festival: 'Diwali' }
    },
    {
        id: 'heatwave_epidemic',
        name: 'Heat Wave + Flu Outbreak',
        description: 'Temperature 42°C + 500 flu cases',
        icon: TrendingUp,
        color: 'orange',
        triggers: { temperature: 42, epidemic: 'Influenza' }
    },
    {
        id: 'festival_surge',
        name: 'Major Festival Surge',
        description: 'Ganesh Chaturthi + Crowd injuries',
        icon: Users,
        color: 'purple',
        triggers: { festival: 'Ganesh Chaturthi' }
    },
    {
        id: 'triple_threat',
        name: 'Triple Threat Crisis',
        description: 'High AQI + Festival + Epidemic (Worst Case)',
        icon: Zap,
        color: 'red',
        triggers: { aqi: 400, festival: 'Diwali', epidemic: 'Dengue' }
    }
];

export const CrisisSimulator = () => {
    const [isSimulating, setIsSimulating] = useState(false);
    const [selectedScenario, setSelectedScenario] = useState<CrisisScenario | null>(null);
    const [simulationSteps, setSimulationSteps] = useState<SimulationStep[]>([]);
    const [impact, setImpact] = useState<any>(null);

    const runSimulation = async (scenario: CrisisScenario) => {
        setSelectedScenario(scenario);
        setIsSimulating(true);
        setSimulationSteps([]);
        setImpact(null);

        // Step 1: Data Agent detects crisis
        await addStep({
            id: 1,
            agent: 'DataAgent',
            action: 'Crisis Detected',
            result: `AQI: ${scenario.triggers.aqi || 'Normal'}, Festival: ${scenario.triggers.festival || 'None'}, Epidemic: ${scenario.triggers.epidemic || 'None'}`,
            timestamp: Date.now(),
            icon: AlertTriangle,
            color: 'blue'
        }, 1000);

        // Step 2: Predictive Agent forecasts
        await addStep({
            id: 2,
            agent: 'PredictiveAgent',
            action: 'Running ML Models',
            result: 'Predicted surge: 180% increase in next 48 hours',
            timestamp: Date.now(),
            icon: TrendingUp,
            color: 'purple'
        }, 1500);

        // Step 3: Planning Agent optimizes
        await addStep({
            id: 3,
            agent: 'PlanningAgent',
            action: 'Optimizing Resources',
            result: 'Recommendation: +15 doctors, +25 nurses, +500 oxygen units',
            timestamp: Date.now(),
            icon: Users,
            color: 'green'
        }, 1500);

        // Step 4: Advisory Agent generates alerts
        await addStep({
            id: 4,
            agent: 'AdvisoryAgent',
            action: 'Generating Advisories',
            result: 'Sent 3,000 SMS alerts, 5,000 emails, 2,000 WhatsApp messages',
            timestamp: Date.now(),
            icon: MessageSquare,
            color: 'amber'
        }, 1500);

        // Step 5: Calculate impact
        await new Promise(resolve => setTimeout(resolve, 1000));
        calculateImpact(scenario);
        setIsSimulating(false);
    };

    const addStep = (step: SimulationStep, delay: number) => {
        return new Promise(resolve => {
            setTimeout(() => {
                setSimulationSteps(prev => [...prev, step]);
                resolve(true);
            }, delay);
        });
    };

    const calculateImpact = (scenario: CrisisScenario) => {
        const baseWaitTime = 6.0; // hours
        const baseBedShortage = 45; // beds
        const baseStockouts = 8; // items

        const withoutAI = {
            waitTime: baseWaitTime,
            bedShortage: baseBedShortage,
            stockouts: baseStockouts,
            patientsAffected: 450
        };

        const withAI = {
            waitTime: baseWaitTime * 0.35, // 65% reduction
            bedShortage: baseBedShortage * 0.15, // 85% reduction
            stockouts: baseStockouts * 0.12, // 88% reduction
            patientsAffected: 450 * 0.25 // 75% fewer affected
        };

        setImpact({ withoutAI, withAI });
    };

    const resetSimulation = () => {
        setSelectedScenario(null);
        setSimulationSteps([]);
        setImpact(null);
        setIsSimulating(false);
    };

    const getColorClasses = (color: string) => {
        const colors = {
            rose: 'bg-rose-500/10 text-rose-500 border-rose-500/20',
            orange: 'bg-orange-500/10 text-orange-500 border-orange-500/20',
            purple: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
            red: 'bg-red-500/10 text-red-500 border-red-500/20',
            blue: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
            green: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
            amber: 'bg-amber-500/10 text-amber-500 border-amber-500/20'
        };
        return colors[color] || colors.blue;
    };

    return (
        <div className="space-y-6">
            {/* Scenario Selection */}
            {!selectedScenario && (
                <Card className="p-6 backdrop-blur-md bg-white/5 border-white/10 shadow-xl">
                    <div className="mb-6">
                        <h3 className="text-2xl font-bold mb-2">🎭 Live Crisis Simulator</h3>
                        <p className="text-muted-foreground">
                            Select a crisis scenario to see how HospAgent's AI agents respond in real-time
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {scenarios.map((scenario) => {
                            const Icon = scenario.icon;
                            return (
                                <motion.div
                                    key={scenario.id}
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                >
                                    <Card
                                        className={`p-6 cursor-pointer border-2 ${getColorClasses(scenario.color)} hover:bg-white/10 transition-all`}
                                        onClick={() => runSimulation(scenario)}
                                    >
                                        <div className="flex items-start gap-4">
                                            <div className={`p-3 rounded-xl ${getColorClasses(scenario.color)}`}>
                                                <Icon className="h-6 w-6" />
                                            </div>
                                            <div className="flex-1">
                                                <h4 className="font-semibold mb-2">{scenario.name}</h4>
                                                <p className="text-sm text-muted-foreground mb-3">{scenario.description}</p>
                                                <Button size="sm" className="w-full">
                                                    <Play className="h-4 w-4 mr-2" />
                                                    Run Simulation
                                                </Button>
                                            </div>
                                        </div>
                                    </Card>
                                </motion.div>
                            );
                        })}
                    </div>
                </Card>
            )}

            {/* Simulation in Progress */}
            {selectedScenario && (
                <>
                    <Card className="p-6 backdrop-blur-md bg-white/5 border-white/10 shadow-xl">
                        <div className="flex items-center justify-between mb-6">
                            <div>
                                <h3 className="text-xl font-bold mb-1">Simulating: {selectedScenario.name}</h3>
                                <p className="text-sm text-muted-foreground">{selectedScenario.description}</p>
                            </div>
                            <Button variant="outline" onClick={resetSimulation} disabled={isSimulating}>
                                <RotateCcw className="h-4 w-4 mr-2" />
                                Reset
                            </Button>
                        </div>

                        {/* Agent Actions */}
                        <div className="space-y-3">
                            <AnimatePresence>
                                {simulationSteps.map((step) => {
                                    const Icon = step.icon;
                                    return (
                                        <motion.div
                                            key={step.id}
                                            initial={{ opacity: 0, x: -50 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            className={`p-4 rounded-xl border ${getColorClasses(step.color)}`}
                                        >
                                            <div className="flex items-start gap-3">
                                                <div className={`p-2 rounded-lg ${getColorClasses(step.color)}`}>
                                                    <Icon className="h-5 w-5" />
                                                </div>
                                                <div className="flex-1">
                                                    <div className="flex items-center justify-between mb-2">
                                                        <span className="font-semibold">{step.agent}</span>
                                                        <Badge variant="outline" className="text-xs">
                                                            Step {step.id}/4
                                                        </Badge>
                                                    </div>
                                                    <p className="text-sm font-medium mb-1">{step.action}</p>
                                                    <p className="text-xs text-muted-foreground">{step.result}</p>
                                                </div>
                                            </div>
                                        </motion.div>
                                    );
                                })}
                            </AnimatePresence>

                            {isSimulating && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="flex items-center justify-center p-8"
                                >
                                    <div className="flex items-center gap-3">
                                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                                        <span className="text-muted-foreground">AI agents working...</span>
                                    </div>
                                </motion.div>
                            )}
                        </div>
                    </Card>

                    {/* Impact Comparison */}
                    {impact && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            <Card className="p-6 backdrop-blur-md bg-white/5 border-white/10 shadow-xl">
                                <h3 className="text-xl font-bold mb-6">📊 Impact Analysis</h3>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {/* Without AI */}
                                    <div className="p-6 rounded-xl bg-rose-500/10 border border-rose-500/20">
                                        <h4 className="font-semibold mb-4 text-rose-500">❌ Without HospAgent</h4>
                                        <div className="space-y-3">
                                            <div>
                                                <p className="text-sm text-muted-foreground">Average Wait Time</p>
                                                <p className="text-2xl font-bold">{impact.withoutAI.waitTime.toFixed(1)} hours</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-muted-foreground">Bed Shortage</p>
                                                <p className="text-2xl font-bold">{impact.withoutAI.bedShortage} beds</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-muted-foreground">Supply Stockouts</p>
                                                <p className="text-2xl font-bold">{impact.withoutAI.stockouts} items</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-muted-foreground">Patients Affected</p>
                                                <p className="text-2xl font-bold">{impact.withoutAI.patientsAffected}</p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* With AI */}
                                    <div className="p-6 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                                        <h4 className="font-semibold mb-4 text-emerald-500">✅ With HospAgent</h4>
                                        <div className="space-y-3">
                                            <div>
                                                <p className="text-sm text-muted-foreground">Average Wait Time</p>
                                                <p className="text-2xl font-bold text-emerald-500">{impact.withAI.waitTime.toFixed(1)} hours</p>
                                                <p className="text-xs text-emerald-500">↓ 65% reduction</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-muted-foreground">Bed Shortage</p>
                                                <p className="text-2xl font-bold text-emerald-500">{Math.round(impact.withAI.bedShortage)} beds</p>
                                                <p className="text-xs text-emerald-500">↓ 85% reduction</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-muted-foreground">Supply Stockouts</p>
                                                <p className="text-2xl font-bold text-emerald-500">{Math.round(impact.withAI.stockouts)} items</p>
                                                <p className="text-xs text-emerald-500">↓ 88% reduction</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-muted-foreground">Patients Affected</p>
                                                <p className="text-2xl font-bold text-emerald-500">{Math.round(impact.withAI.patientsAffected)}</p>
                                                <p className="text-xs text-emerald-500">↓ 75% reduction</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div className="mt-6 p-4 rounded-xl bg-blue-500/10 border border-blue-500/20">
                                    <p className="text-center font-semibold text-blue-500">
                                        🎯 HospAgent prevented a healthcare crisis and saved an estimated 337 patients from delays
                                    </p>
                                </div>
                            </Card>
                        </motion.div>
                    )}
                </>
            )}
        </div>
    );
};
