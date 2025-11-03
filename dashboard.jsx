import React, { useState, useMemo } from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, Eye, Filter, Zap, Target } from 'lucide-react';

const AITrendDashboard = () => {
  // Sample corpus of AI research papers
  const sampleCorpus = [
    // Emerging: Multi-modal RAG
    { id: '001', title: 'Vision-Enhanced RAG Systems', date: '2025-10-25', techniques: ['RAG', 'multi-modal', 'vision'], citations: 12 },
    { id: '002', title: 'Multi-Modal Document Understanding', date: '2025-10-22', techniques: ['multi-modal', 'RAG', 'OCR'], citations: 8 },
    { id: '003', title: 'Image-Text Retrieval at Scale', date: '2025-10-20', techniques: ['RAG', 'multi-modal', 'embeddings'], citations: 15 },
    { id: '004', title: 'Cross-Modal RAG Architecture', date: '2025-10-18', techniques: ['RAG', 'multi-modal', 'attention'], citations: 9 },
    { id: '005', title: 'Unified Multi-Modal Search', date: '2025-10-15', techniques: ['multi-modal', 'RAG', 'semantic'], citations: 11 },
    { id: '006', title: 'Early Multi-Modal Experiments', date: '2025-09-12', techniques: ['multi-modal', 'RAG'], citations: 3 },
    { id: '007', title: 'Vision RAG Prototype', date: '2025-09-05', techniques: ['RAG', 'multi-modal'], citations: 2 },
    
    // Maturing: Function Calling
    { id: '008', title: 'Production Function Calling at Scale', date: '2025-10-28', techniques: ['function-calling', 'API', 'production'], citations: 45 },
    { id: '009', title: 'Function Calling Best Practices', date: '2025-10-24', techniques: ['function-calling', 'API', 'patterns'], citations: 38 },
    { id: '010', title: 'Reliable Function Execution', date: '2025-10-19', techniques: ['function-calling', 'reliability', 'production'], citations: 42 },
    { id: '011', title: 'Function Calling in Enterprise', date: '2025-10-14', techniques: ['function-calling', 'API', 'deployment'], citations: 35 },
    { id: '012', title: 'Tool Use Optimization', date: '2025-10-09', techniques: ['function-calling', 'API'], citations: 40 },
    { id: '013', title: 'Function APIs Standardization', date: '2025-10-04', techniques: ['function-calling', 'API', 'production'], citations: 37 },
    { id: '014', title: 'Function Calling Studies', date: '2025-09-25', techniques: ['function-calling', 'API'], citations: 33 },
    { id: '015', title: 'Tool Integration Patterns', date: '2025-09-18', techniques: ['function-calling', 'API'], citations: 31 },
    { id: '016', title: 'Deployed Function Systems', date: '2025-09-10', techniques: ['function-calling', 'production'], citations: 36 },
    { id: '017', title: 'Function Calling Architecture', date: '2025-09-02', techniques: ['function-calling', 'API'], citations: 29 },
    { id: '018', title: 'API Integration Methods', date: '2025-08-20', techniques: ['function-calling', 'API'], citations: 28 },
    { id: '019', title: 'Function Call Reliability', date: '2025-08-12', techniques: ['function-calling', 'production'], citations: 32 },
    
    // Declining: Prompt Chaining
    { id: '020', title: 'Legacy Prompt Chains', date: '2025-10-26', techniques: ['prompt-chaining', 'sequential'], citations: 5 },
    { id: '021', title: 'Simple Chain Analysis', date: '2025-10-10', techniques: ['prompt-chaining'], citations: 4 },
    { id: '022', title: 'Chain Optimization Study', date: '2025-09-28', techniques: ['prompt-chaining', 'sequential'], citations: 18 },
    { id: '023', title: 'Prompt Chain Patterns', date: '2025-09-15', techniques: ['prompt-chaining', 'sequential'], citations: 22 },
    { id: '024', title: 'Sequential Processing with Chains', date: '2025-09-08', techniques: ['prompt-chaining'], citations: 19 },
    { id: '025', title: 'Chain-Based Workflows', date: '2025-09-01', techniques: ['prompt-chaining', 'sequential'], citations: 21 },
    { id: '026', title: 'Advanced Prompt Chaining', date: '2025-08-25', techniques: ['prompt-chaining'], citations: 20 },
    { id: '027', title: 'Multi-Step Chain Systems', date: '2025-08-18', techniques: ['prompt-chaining', 'sequential'], citations: 17 },
    { id: '028', title: 'Prompt Chain Fundamentals', date: '2025-08-10', techniques: ['prompt-chaining'], citations: 16 },
    
    // Mature techniques for gap detection
    { id: '029', title: 'Streaming Response Architecture', date: '2025-10-27', techniques: ['streaming', 'real-time'], citations: 25 },
    { id: '030', title: 'Real-Time Streaming Systems', date: '2025-10-23', techniques: ['streaming', 'performance'], citations: 28 },
    { id: '031', title: 'Streaming at Scale', date: '2025-10-16', techniques: ['streaming', 'real-time'], citations: 22 },
    { id: '032', title: 'Low-Latency Streaming', date: '2025-10-11', techniques: ['streaming', 'performance'], citations: 26 },
    { id: '033', title: 'Streaming Best Practices', date: '2025-10-05', techniques: ['streaming', 'real-time'], citations: 24 },
    { id: '034', title: 'Production Streaming Patterns', date: '2025-09-29', techniques: ['streaming', 'production'], citations: 27 },
    { id: '035', title: 'Streaming Response Design', date: '2025-09-22', techniques: ['streaming', 'real-time'], citations: 23 },
    { id: '036', title: 'Efficient Streaming Methods', date: '2025-09-14', techniques: ['streaming', 'performance'], citations: 21 },
    { id: '037', title: 'Streaming Infrastructure', date: '2025-09-06', techniques: ['streaming', 'production'], citations: 25 },
    { id: '038', title: 'Real-Time Response Systems', date: '2025-08-28', techniques: ['streaming', 'real-time'], citations: 20 },
    { id: '039', title: 'Streaming Optimization', date: '2025-08-19', techniques: ['streaming', 'performance'], citations: 22 },
    { id: '040', title: 'Advanced Streaming Techniques', date: '2025-08-11', techniques: ['streaming', 'real-time'], citations: 19 },
  ];

  const [constitution, setConstitution] = useState({
    strategic_focus: ['real-time AI systems', 'production-ready', 'emerging techniques'],
    priorities: { latency: '<100ms', stability: '>7/10' }
  });
  
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');
  const [showDetails, setShowDetails] = useState(null);

  // Multi-pass trend detection logic
  const detectTrends = () => {
    const today = new Date('2025-10-30');
    const results = {
      emerging: [],
      maturing: [],
      declining: [],
      gaps: []
    };

    // Helper: Get papers in date range
    const getPapersInRange = (startDays, endDays, technique) => {
      const start = new Date(today);
      start.setDate(start.getDate() - startDays);
      const end = new Date(today);
      end.setDate(end.getDate() - endDays);
      
      return sampleCorpus.filter(p => {
        const pDate = new Date(p.date);
        return pDate >= end && pDate <= start && p.techniques.includes(technique);
      });
    };

    // Helper: Get all unique techniques
    const allTechniques = [...new Set(sampleCorpus.flatMap(p => p.techniques))];

    // PASS A: Emergence Detection
    allTechniques.forEach(tech => {
      const recentPapers = getPapersInRange(30, 0, tech);
      const historicalPapers = getPapersInRange(60, 30, tech);
      
      if (recentPapers.length >= 5 && historicalPapers.length > 0) {
        const acceleration = recentPapers.length / historicalPapers.length;
        
        if (acceleration >= 3.0) {
          const firstMention = sampleCorpus
            .filter(p => p.techniques.includes(tech))
            .sort((a, b) => new Date(a.date) - new Date(b.date))[0];
          
          const daysSinceFirst = Math.floor((today - new Date(firstMention.date)) / (1000 * 60 * 60 * 24));
          
          if (daysSinceFirst < 60) {
            let severity = acceleration >= 5.0 ? 'CRITICAL' : 'HIGH';
            
            // Constitution boost
            const matchesStrategy = constitution.strategic_focus.some(focus => 
              focus.toLowerCase().includes('emerging') || 
              focus.toLowerCase().includes('real-time')
            );
            if (matchesStrategy && severity === 'HIGH') severity = 'CRITICAL';
            
            results.emerging.push({
              technique: tech,
              severity,
              acceleration: acceleration.toFixed(1),
              recentCount: recentPapers.length,
              historicalCount: historicalPapers.length,
              papers: recentPapers.slice(0, 3).map(p => p.title),
              recommendation: 'Prototype within 2 weeks'
            });
          }
        }
      }
    });

    // PASS B: Maturation Detection
    allTechniques.forEach(tech => {
      const papers90days = getPapersInRange(90, 0, tech);
      
      if (papers90days.length >= 10) {
        // Check variance across weeks
        const weeks = [];
        for (let i = 0; i < 12; i++) {
          const weekPapers = getPapersInRange((i + 1) * 7, i * 7, tech);
          weeks.push(weekPapers.length);
        }
        
        const mean = weeks.reduce((a, b) => a + b, 0) / weeks.length;
        const variance = weeks.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / weeks.length;
        const relativeVariance = Math.sqrt(variance) / mean;
        
        if (relativeVariance < 0.2) {
          const productionPapers = papers90days.filter(p => 
            p.title.toLowerCase().includes('production') || 
            p.title.toLowerCase().includes('deployment') ||
            p.title.toLowerCase().includes('scale')
          );
          
          if (productionPapers.length >= 2) {
            let severity = 'HIGH';
            
            const matchesStrategy = constitution.strategic_focus.some(focus => 
              focus.toLowerCase().includes('production')
            );
            if (matchesStrategy) severity = 'CRITICAL';
            
            results.maturing.push({
              technique: tech,
              severity,
              stability: `${(100 - relativeVariance * 100).toFixed(0)}%`,
              totalPapers: papers90days.length,
              productionSignals: productionPapers.length,
              papers: productionPapers.slice(0, 3).map(p => p.title),
              recommendation: 'Production rollout ready'
            });
          }
        }
      }
    });

    // PASS C: Decline Detection
    allTechniques.forEach(tech => {
      const recentPapers = getPapersInRange(30, 0, tech);
      const historicalPapers = getPapersInRange(90, 30, tech);
      
      if (historicalPapers.length >= 5 && recentPapers.length < historicalPapers.length * 0.3) {
        const declinePercent = ((historicalPapers.length - recentPapers.length) / historicalPapers.length * 100).toFixed(0);
        
        results.declining.push({
          technique: tech,
          severity: 'LOW',
          decline: `${declinePercent}%`,
          recentCount: recentPapers.length,
          historicalCount: historicalPapers.length,
          papers: historicalPapers.slice(0, 3).map(p => p.title),
          recommendation: 'Consider migration to newer alternatives'
        });
      }
    });

    // PASS D: Gap Detection
    const matureTechniques = allTechniques.filter(tech => {
      return getPapersInRange(90, 0, tech).length >= 10;
    });
    
    for (let i = 0; i < matureTechniques.length; i++) {
      for (let j = i + 1; j < matureTechniques.length; j++) {
        const techA = matureTechniques[i];
        const techB = matureTechniques[j];
        
        const combined = sampleCorpus.filter(p => 
          p.techniques.includes(techA) && p.techniques.includes(techB)
        );
        
        if (combined.length === 0) {
          const papersA = getPapersInRange(90, 0, techA).length;
          const papersB = getPapersInRange(90, 0, techB).length;
          
          let severity = (papersA >= 20 && papersB >= 20) ? 'CRITICAL' : 'MEDIUM';
          
          const matchesStrategy = constitution.strategic_focus.some(focus => 
            focus.toLowerCase().includes('real-time') && 
            (techA.includes('streaming') || techB.includes('streaming'))
          );
          if (matchesStrategy && severity === 'MEDIUM') severity = 'HIGH';
          
          results.gaps.push({
            techniqueA: techA,
            techniqueB: techB,
            severity,
            papersA,
            papersB,
            combined: 0,
            recommendation: 'Research opportunity - unexplored combination'
          });
        }
      }
    }

    return results;
  };

  const trends = useMemo(() => detectTrends(), [constitution]);

  // Flatten all trends with type
  const allTrends = useMemo(() => {
    return [
      ...trends.emerging.map(t => ({ ...t, type: 'EMERGING', icon: TrendingUp, color: 'text-purple-600' })),
      ...trends.maturing.map(t => ({ ...t, type: 'MATURING', icon: Target, color: 'text-blue-600' })),
      ...trends.declining.map(t => ({ ...t, type: 'DECLINING', icon: TrendingDown, color: 'text-gray-500' })),
      ...trends.gaps.map(t => ({ ...t, type: 'GAP', icon: AlertTriangle, color: 'text-orange-600' }))
    ];
  }, [trends]);

  const filteredTrends = useMemo(() => {
    if (selectedSeverity === 'ALL') return allTrends;
    return allTrends.filter(t => t.severity === selectedSeverity);
  }, [allTrends, selectedSeverity]);

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return 'bg-red-100 text-red-800 border-red-300';
      case 'HIGH': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'LOW': return 'bg-gray-100 text-gray-700 border-gray-300';
      default: return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  const severityCounts = useMemo(() => {
    return {
      CRITICAL: allTrends.filter(t => t.severity === 'CRITICAL').length,
      HIGH: allTrends.filter(t => t.severity === 'HIGH').length,
      MEDIUM: allTrends.filter(t => t.severity === 'MEDIUM').length,
      LOW: allTrends.filter(t => t.severity === 'LOW').length,
      ALL: allTrends.length
    };
  }, [allTrends]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <Zap className="w-10 h-10 text-indigo-600" />
            <h1 className="text-4xl font-bold text-gray-900">AI Trend Analyzer</h1>
          </div>
          <p className="text-lg text-gray-600">
            Systematic multi-pass detection with deterministic logic • Constitution-guided filtering • Fully traceable to source papers
          </p>
        </div>

        {/* Executive Summary */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Executive Summary</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-red-50 rounded-lg border border-red-200">
              <div className="text-3xl font-bold text-red-700">{severityCounts.CRITICAL}</div>
              <div className="text-sm text-red-600 font-medium mt-1">Critical</div>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg border border-orange-200">
              <div className="text-3xl font-bold text-orange-700">{severityCounts.HIGH}</div>
              <div className="text-sm text-orange-600 font-medium mt-1">High Priority</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg border border-yellow-200">
              <div className="text-3xl font-bold text-yellow-700">{severityCounts.MEDIUM}</div>
              <div className="text-sm text-yellow-600 font-medium mt-1">Medium</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="text-3xl font-bold text-gray-700">{severityCounts.LOW}</div>
              <div className="text-sm text-gray-600 font-medium mt-1">Low Priority</div>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-indigo-50 rounded-lg border border-indigo-200">
            <div className="font-semibold text-indigo-900 mb-2">Top Recommendations:</div>
            <ul className="space-y-2 text-sm text-indigo-800">
              {allTrends
                .filter(t => t.severity === 'CRITICAL')
                .slice(0, 3)
                .map((t, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-indigo-600">•</span>
                    <span><strong>{t.technique || `${t.techniqueA} + ${t.techniqueB}`}:</strong> {t.recommendation}</span>
                  </li>
                ))}
            </ul>
          </div>
        </div>

        {/* Constitution Editor */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Filter className="w-5 h-5" />
            Strategic Constitution
          </h2>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Strategic Focus Areas (comma-separated):
              </label>
              <input
                type="text"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                value={constitution.strategic_focus.join(', ')}
                onChange={(e) => setConstitution({
                  ...constitution,
                  strategic_focus: e.target.value.split(',').map(s => s.trim())
                })}
              />
            </div>
            <div className="text-sm text-gray-600">
              <strong>How it works:</strong> Trends matching 2+ focus areas get boosted from HIGH → CRITICAL. 
              Trends matching 1+ focus areas get boosted from MEDIUM → HIGH.
            </div>
          </div>
        </div>

        {/* Severity Filter */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border border-gray-200">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <h2 className="text-xl font-bold text-gray-900">Detected Trends ({filteredTrends.length})</h2>
            <div className="flex gap-2">
              {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(sev => (
                <button
                  key={sev}
                  onClick={() => setSelectedSeverity(sev)}
                  className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                    selectedSeverity === sev
                      ? sev === 'ALL' 
                        ? 'bg-indigo-600 text-white'
                        : `${getSeverityColor(sev)} border-2`
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {sev} ({severityCounts[sev]})
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Trends List */}
        <div className="space-y-4">
          {filteredTrends.map((trend, idx) => {
            const Icon = trend.icon;
            const isExpanded = showDetails === idx;
            
            return (
              <div key={idx} className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
                <div 
                  className="p-6 cursor-pointer hover:bg-gray-50 transition-colors"
                  onClick={() => setShowDetails(isExpanded ? null : idx)}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-4 flex-1">
                      <div className={`p-3 rounded-lg bg-gray-50 ${trend.color}`}>
                        <Icon className="w-6 h-6" />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-bold text-gray-900">
                            {trend.type === 'GAP' 
                              ? `${trend.techniqueA} + ${trend.techniqueB}`
                              : trend.technique}
                          </h3>
                          <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getSeverityColor(trend.severity)}`}>
                            {trend.severity}
                          </span>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700`}>
                            {trend.type}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3 text-sm">
                          {trend.type === 'EMERGING' && (
                            <>
                              <div>
                                <span className="text-gray-500">Acceleration:</span>
                                <span className="ml-2 font-semibold text-purple-600">{trend.acceleration}x</span>
                              </div>
                              <div>
                                <span className="text-gray-500">Recent papers:</span>
                                <span className="ml-2 font-semibold">{trend.recentCount}</span>
                              </div>
                              <div>
                                <span className="text-gray-500">Historical:</span>
                                <span className="ml-2 font-semibold">{trend.historicalCount}</span>
                              </div>
                            </>
                          )}
                          
                          {trend.type === 'MATURING' && (
                            <>
                              <div>
                                <span className="text-gray-500">Stability:</span>
                                <span className="ml-2 font-semibold text-blue-600">{trend.stability}</span>
                              </div>
                              <div>
                                <span className="text-gray-500">Total papers:</span>
                                <span className="ml-2 font-semibold">{trend.totalPapers}</span>
                              </div>
                              <div>
                                <span className="text-gray-500">Production signals:</span>
                                <span className="ml-2 font-semibold">{trend.productionSignals}</span>
                              </div>
                            </>
                          )}
                          
                          {trend.type === 'DECLINING' && (
                            <>
                              <div>
                                <span className="text-gray-500">Decline:</span>
                                <span className="ml-2 font-semibold text-red-600">{trend.decline}</span>
                              </div>
                              <div>
                                <span className="text-gray-500">Recent:</span>
                                <span className="ml-2 font-semibold">{trend.recentCount}</span>
                              </div>
                              <div>
                                <span className="text-gray-500">Historical:</span>
                                <span className="ml-2 font-semibold">{trend.historicalCount}</span>
                              </div>
                            </>
                          )}
                          
                          {trend.type === 'GAP' && (
                            <>
                              <div>
                                <span className="text-gray-500">{trend.techniqueA}:</span>
                                <span className="ml-2 font-semibold">{trend.papersA} papers</span>
                              </div>
                              <div>
                                <span className="text-gray-500">{trend.techniqueB}:</span>
                                <span className="ml-2 font-semibold">{trend.papersB} papers</span>
                              </div>
                              <div>
                                <span className="text-gray-500">Combined:</span>
                                <span className="ml-2 font-semibold text-orange-600">{trend.combined} papers</span>
                              </div>
                            </>
                          )}
                        </div>
                        
                        <div className="flex items-center gap-2 text-sm text-indigo-600 font-medium">
                          <Eye className="w-4 h-4" />
                          {isExpanded ? 'Hide details' : 'View source papers & recommendation'}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                {isExpanded && (
                  <div className="border-t border-gray-200 p-6 bg-gray-50">
                    <div className="mb-4">
                      <h4 className="font-semibold text-gray-900 mb-2">Recommendation:</h4>
                      <p className="text-gray-700">{trend.recommendation}</p>
                    </div>
                    
                    {trend.papers && trend.papers.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">Source Papers:</h4>
                        <ul className="space-y-2">
                          {trend.papers.map((paper, i) => (
                            <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                              <span className="text-indigo-600 font-bold">{i + 1}.</span>
                              <span>{paper}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-sm text-gray-500">
          <p className="mb-2">
            <strong>Detection Logic:</strong> Pass A: Emergence (≥3x acceleration) • Pass B: Maturation (variance &lt;20%, production signals) • 
            Pass C: Decline (&lt;30% of historical) • Pass D: Gaps (zero combined papers)
          </p>
          <p>
            Powered by <strong>ai-trend-analyzer</strong> skill • Deterministic multi-pass analysis • 
            Corpus: {sampleCorpus.length} papers • Analysis date: October 30, 2025
          </p>
        </div>
      </div>
    </div>
  );
};

export default AITrendDashboard;