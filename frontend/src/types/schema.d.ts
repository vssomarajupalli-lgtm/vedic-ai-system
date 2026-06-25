export interface ReportSectionData {
    title: string;
    summary_text: string;
    data_points: Record<string, any>;
    warnings: string[];
}

export interface FinalReportSchema {
    report_version: string;
    generated_at: string;
    client_profile: Record<string, string>;
    executive_summary: ReportSectionData;
    master_probability: ReportSectionData;
    natal_promise_analysis: ReportSectionData;
    planet_analysis: ReportSectionData;
    house_analysis: ReportSectionData;
    yoga_analysis: ReportSectionData;
    dasha_analysis: ReportSectionData;
    transit_analysis: ReportSectionData;
    ashtakavarga_analysis: ReportSectionData;
    question_responses: Record<string, any>[];
}

export interface ChartProcessResponse {
    status: string;
    final_score: number;
    probability_grade: string;
    breakdown: Record<string, any>;
    yogas: any[];
}

export interface QuestionResponse {
    question_id: string;
    answer_text: string;
    referenced_yogas: string[];
}

export interface StructuredQuestionResponse {
    question_id: string;
    results: any[]; // Using any[] to avoid circular dependency with QuestionResultCard
}
