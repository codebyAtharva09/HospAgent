import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useEffect, useState } from "react";
import { Activity, Brain, Users, Package, MessageSquare, Zap } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface AgentActivity {
    id: string;
    agent: string;
    action: string;
    status: 'active' | 'completed' | 'waiting';
    timestamp: string;
    details?: string;
}

interface AgentStatus {
    name: string;
    status: 'active' | 'idle' | 'processing';
    currentTask: string;
    tasksCompleted: number;
    icon: any;
    color: string;
}

export const AgentVisualization = () => {
    const [activities, setActivities] = useState<AgentActivity[]>([]);
    const [agents, setAgents] = useState<AgentStatus[]>([
        {
            name: 'DataAgent',
            status: 'idle',
            currentTask: 'Monitoring data sources',
            tasksCompleted: 0,
            icon: Activity,
            color: 'blue'
        },
        {
            name: 'PredictiveAgent',
            status: 'idle',
            currentTask: 'Ready to predict',
            tasksCompleted: 0,
            icon: Brain,
            color: 'purple'
        },
        {
            name: 'PlanningAgent',
            status: 'idle',
            currentTask: 'Awaiting predictions',
            tasksCompleted: 0,
            icon: Users,
            color: 'green'
        },
        {
            name: 'AdvisoryAgent',
            status: 'idle',
            currentTask: 'Monitoring risks',
            tasksCompleted: 0,
            icon: MessageSquare,
            color: 'amber'
        }
    ]);

    useEffect(() => {
        // Simulate agent activities
        const simulateActivity = () => {
            const agentNames = ['DataAgent', 'PredictiveAgent', 'PlanningAgent', 'AdvisoryAgent'];
            const actions = {
                DataAgent: [
                    'Fetching AQI data from OpenAQ',
                    'Retrieving weather forecast',
                    'Checking festival calendar',
                    'Monitoring epidemic trends',
                    'Validating data quality'
                ],
                PredictiveAgent: [
                    'Analyzing surge patterns',
                    'Running ML models',
                    'Calculating confidence intervals',
                    'Generating 7-day forecast',
                    'Updating predictions'
                ],
                PlanningAgent: [
                    'Optimizing staff allocation',
                    'Checking inventory levels',
                    'Calculating bed requirements',
                    'Generating recommendations',
                    'Resolving resource conflicts'
                ],
                AdvisoryAgent: [
                    'Assessing health risks',
                    'Generating advisories',
                    'Preparing multi-channel alerts',
                    'Personalizing messages',
                    'Scheduling notifications'
                ]
            };

            const randomAgent = agentNames[Math.floor(Math.random() * agentNames.length)];
            const randomAction = actions[randomAgent][Math.floor(Math.random() * actions[randomAgent].length)];

            const newActivity: AgentActivity = {
                id: `${Date.now()}-${Math.random()}`,
                agent: randomAgent,
                action: randomAction,
                status: 'active',
                timestamp: new Date().toISOString()
            };

            setActivities(prev => [newActivity, ...prev.slice(0, 9)]);

            // Update agent status
            setAgents(prev => prev.map(agent => {
                if (agent.name === randomAgent) {
                    return {
                        ...agent,
                        status: 'processing',
                        currentTask: randomAction,
                        tasksCompleted: agent.tasksCompleted + 1
                    };
                }
                return agent;
            }));

            // Mark as completed after 2 seconds
            setTimeout(() => {
                setActivities(prev => prev.map(act =>
                    act.id === newActivity.id ? { ...act, status: 'completed' } : act
                ));
                setAgents(prev => prev.map(agent =>
                    agent.name === randomAgent ? { ...agent, status: 'idle' } : agent
                ));
            }, 2000);
        };

        // Run simulation every 3 seconds
        const interval = setInterval(simulateActivity, 3000);
        simulateActivity(); // Run immediately

        return () => clearInterval(interval);
    }, []);

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active': return 'bg-blue-500';
            case 'processing': return 'bg-purple-500 animate-pulse';
            case 'completed': return 'bg-emerald-500';
            case 'idle': return 'bg-gray-500';
            default: return 'bg-gray-500';
        }
    };

    const getAgentColor = (color: string) => {
        const colors = {
            blue: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
            purple: 'text-purple-500 bg-purple-500/10 border-purple-500/20',
            green: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20',
            amber: 'text-amber-500 bg-amber-500/10 border-amber-500/20'
        };
        return colors[color] || colors.blue;
    };

    return (
        <div className="space-y-6">
            {/* Agent Status Grid */}
            <Card className="p-6 backdrop-blur-md bg-white/5 border-white/10 shadow-xl">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold flex items-center gap-2">
                        <Zap className="h-5 w-5 text-yellow-500" />
                        Live Agent Activity
                    </h3>
                    <Badge variant="outline" className="bg-emerald-500/10 text-emerald-500 border-emerald-500/20">
                        <span className="relative flex h-2 w-2 mr-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                        </span>
                        All Systems Active
                    </Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {agents.map((agent) => {
                        const Icon = agent.icon;
                        return (
                            <motion.div
                                key={agent.name}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={`p-4 rounded-xl border ${getAgentColor(agent.color)} transition-all duration-300`}
                            >
                                <div className="flex items-center gap-3 mb-3">
                                    <div className={`p-2 rounded-lg ${getAgentColor(agent.color)}`}>
                                        <Icon className="h-5 w-5" />
                                    </div>
                                    <div className="flex-1">
                                        <p className="font-semibold text-sm">{agent.name}</p>
                                        <div className="flex items-center gap-2 mt-1">
                                            <span className={`h-2 w-2 rounded-full ${getStatusColor(agent.status)}`}></span>
                                            <span className="text-xs text-muted-foreground capitalize">{agent.status}</span>
                                        </div>
                                    </div>
                                </div>
                                <p className="text-xs text-muted-foreground mb-2">{agent.currentTask}</p>
                                <div className="flex items-center justify-between text-xs">
                                    <span className="text-muted-foreground">Tasks</span>
                                    <span className="font-semibold">{agent.tasksCompleted}</span>
                                </div>
                            </motion.div>
                        );
                    })}
                </div>
            </Card>

            {/* Activity Feed */}
            <Card className="p-6 backdrop-blur-md bg-white/5 border-white/10 shadow-xl">
                <h3 className="text-lg font-semibold mb-4">Recent Agent Actions</h3>
                <div className="space-y-2 max-h-[400px] overflow-y-auto">
                    <AnimatePresence>
                        {activities.map((activity) => (
                            <motion.div
                                key={activity.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 20 }}
                                className="flex items-center gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors border border-white/5"
                            >
                                <span className={`h-2 w-2 rounded-full flex-shrink-0 ${getStatusColor(activity.status)}`}></span>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2">
                                        <span className="font-semibold text-sm">{activity.agent}</span>
                                        <span className="text-xs text-muted-foreground">
                                            {new Date(activity.timestamp).toLocaleTimeString()}
                                        </span>
                                    </div>
                                    <p className="text-sm text-muted-foreground truncate">{activity.action}</p>
                                </div>
                                {activity.status === 'completed' && (
                                    <Badge variant="outline" className="bg-emerald-500/10 text-emerald-500 border-emerald-500/20 text-xs">
                                        Done
                                    </Badge>
                                )}
                                {activity.status === 'active' && (
                                    <Badge variant="outline" className="bg-blue-500/10 text-blue-500 border-blue-500/20 text-xs">
                                        Running
                                    </Badge>
                                )}
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>
            </Card>
        </div>
    );
};
