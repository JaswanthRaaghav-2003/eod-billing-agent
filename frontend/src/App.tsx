import React, { useState, useEffect } from 'react';
import { Layout } from './components/Layout';
import { EODReconciliation } from './components/EODReconciliation';
import { AnalyticsView } from './components/AnalyticsView';
import { AINarrativeSummary } from './components/AINarrativeSummary';
import { IngestionModal } from './components/IngestionModal';
import { ValidationErrorsModal } from './components/ValidationErrorsModal';
import { SettingsModal } from './components/SettingsModal';
import { 
  fetchAvailableDays, 
  fetchReconciliation, 
  fetchAnalytics, 
  fetchNarrative,
  generateNarrativeCustom,
  seedSampleData 
} from './services/api';
import { 
  ReconciliationReport, 
  AnalyticsReport, 
  NarrativeReport, 
  DaySummary,
  ValidationErrorDetail 
} from './types';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<'reconciliation' | 'analytics' | 'narrative'>('reconciliation');
  const [selectedDate, setSelectedDate] = useState<string>('2026-07-27');
  const [availableDays, setAvailableDays] = useState<DaySummary[]>([]);
  
  // Data states
  const [reconciliation, setReconciliation] = useState<ReconciliationReport | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsReport | null>(null);
  const [narrative, setNarrative] = useState<NarrativeReport | null>(null);

  // Loading & error states
  const [loadingRecon, setLoadingRecon] = useState(false);
  const [loadingAnalytics, setLoadingAnalytics] = useState(false);
  const [loadingNarrative, setLoadingNarrative] = useState(false);
  const [errorRecon, setErrorRecon] = useState<string | null>(null);
  const [errorAnalytics, setErrorAnalytics] = useState<string | null>(null);
  const [errorNarrative, setErrorNarrative] = useState<string | null>(null);

  // Modals
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isValidationErrorsOpen, setIsValidationErrorsOpen] = useState(false);

  // API Keys
  const [geminiKey, setGeminiKey] = useState<string>(() => localStorage.getItem('swasthiq_gemini_key') || '');
  const [openaiKey, setOpenaiKey] = useState<string>(() => localStorage.getItem('swasthiq_openai_key') || '');

  // Pre-configured validation errors for sample date 2026-07-27
  const sampleValidationErrors: ValidationErrorDetail[] = [
    {
      row_index: 19,
      visit_id: 'V-20260727-019',
      field: 'payment_mode',
      error: "Missing required field 'payment_mode'.",
      actionable_guidance: "Specify a valid payment_mode ('cash', 'card', or 'upi'). Record was safely skipped during ingestion."
    }
  ];

  // Initial load: fetch days
  const loadDays = async () => {
    try {
      let days = await fetchAvailableDays();
      if (!days || days.length === 0) {
        await seedSampleData();
        days = await fetchAvailableDays();
      }
      setAvailableDays(days);
    } catch (e: any) {
      console.error('Error fetching days:', e);
    }
  };

  useEffect(() => {
    loadDays();
  }, []);

  // When selectedDate changes, load all 3 datasets
  useEffect(() => {
    if (!selectedDate) return;

    // Load Reconciliation
    setLoadingRecon(true);
    setErrorRecon(null);
    fetchReconciliation(selectedDate)
      .then((data) => setReconciliation(data))
      .catch((err) => setErrorRecon(err.message))
      .finally(() => setLoadingRecon(false));

    // Load Analytics
    setLoadingAnalytics(true);
    setErrorAnalytics(null);
    fetchAnalytics(selectedDate)
      .then((data) => setAnalytics(data))
      .catch((err) => setErrorAnalytics(err.message))
      .finally(() => setLoadingAnalytics(false));

    // Load Narrative
    setLoadingNarrative(true);
    setErrorNarrative(null);
    fetchNarrative(selectedDate)
      .then((data) => setNarrative(data))
      .catch((err) => setErrorNarrative(err.message))
      .finally(() => setLoadingNarrative(false));
  }, [selectedDate]);

  const handleRegenerateNarrative = async (provider: string) => {
    setLoadingNarrative(true);
    setErrorNarrative(null);
    try {
      const activeKey = provider === 'gemini' ? geminiKey : provider === 'openai' ? openaiKey : undefined;
      const res = await generateNarrativeCustom({
        date: selectedDate,
        provider,
        apiKey: activeKey
      });
      setNarrative(res);
    } catch (err: any) {
      setErrorNarrative(err.message);
    } finally {
      setLoadingNarrative(false);
    }
  };

  const handleResetData = async () => {
    try {
      await seedSampleData();
      await loadDays();
      setSelectedDate('2026-07-27');
    } catch (e) {
      console.error('Error resetting data:', e);
    }
  };

  const clinicName = reconciliation?.clinic_name || 'Mehta Multi-Speciality Clinic ? Kanpur, Uttar Pradesh';

  return (
    <Layout
      currentTab={currentTab}
      setCurrentTab={setCurrentTab}
      selectedDate={selectedDate}
      setSelectedDate={setSelectedDate}
      availableDays={availableDays}
      onOpenUpload={() => setIsUploadOpen(true)}
      onOpenSettings={() => setIsSettingsOpen(true)}
      onResetData={handleResetData}
      clinicName={clinicName}
      hasValidationError={selectedDate === '2026-07-27'}
      onViewValidationErrors={() => setIsValidationErrorsOpen(true)}
    >
      {/* Screen 1: EOD Reconciliation */}
      {currentTab === 'reconciliation' && (
        <EODReconciliation
          report={reconciliation}
          loading={loadingRecon}
          error={errorRecon}
        />
      )}

      {/* Screen 2: Analytics */}
      {currentTab === 'analytics' && (
        <AnalyticsView
          report={analytics}
          loading={loadingAnalytics}
          error={errorAnalytics}
        />
      )}

      {/* Screen 3: AI Narrative Summary */}
      {currentTab === 'narrative' && (
        <AINarrativeSummary
          narrative={narrative}
          loading={loadingNarrative}
          onRegenerate={handleRegenerateNarrative}
          error={errorNarrative}
        />
      )}

      {/* Ingestion Upload Modal */}
      <IngestionModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onSuccess={(newDate) => {
          setIsUploadOpen(false);
          loadDays();
          setSelectedDate(newDate);
        }}
      />

      {/* Validation Errors Inspector Modal */}
      <ValidationErrorsModal
        isOpen={isValidationErrorsOpen}
        onClose={() => setIsValidationErrorsOpen(false)}
        errors={sampleValidationErrors}
        dateStr={selectedDate}
      />

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        geminiKey={geminiKey}
        setGeminiKey={setGeminiKey}
        openaiKey={openaiKey}
        setOpenaiKey={setOpenaiKey}
      />
    </Layout>
  );
};

export default App;
