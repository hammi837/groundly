export type MeResponse = {
  id: string;
  email: string;
  tenant: {
    id: string;
    name: string;
    bot_name: string;
    primary_color: string;
  };
};

export type Document = {
  id: string;
  source_type: string;
  source_name: string;
  status: string;
  error_message: string | null;
  chunk_count: number;
  bytes: number | null;
  created_at: string;
  updated_at: string;
};

export type DocumentContent = {
  id: string;
  source_type: string;
  source_name: string;
  status: string;
  text: string;
  question: string | null;
  answer: string | null;
};

export type ConversationListItem = {
  id: string;
  visitor_id: string;
  visitor_email: string | null;
  started_at: string;
  last_message_at: string;
  message_count: number;
  had_fallback: boolean;
};

export type Message = {
  id: string;
  role: string;
  content: string;
  cited_chunk_ids: string[];
  was_fallback: boolean;
  created_at: string;
  citations: { chunk_id: string; document: string; excerpt: string; page?: number }[];
};

export type ConversationDetail = {
  id: string;
  visitor_id: string;
  visitor_email: string | null;
  started_at: string;
  last_message_at: string;
  messages: Message[];
};

export type Lead = {
  id: string;
  email: string;
  name: string | null;
  phone: string | null;
  question: string;
  status: string;
  conversation_id: string;
  created_at: string;
};

export type Settings = {
  business_name: string;
  bot_name: string;
  primary_color: string;
  welcome_message: string;
  starter_questions: string[];
  allowed_origins: string[];
  rate_limit_rpm: number;
  webhook_url: string | null;
  api_key_masked: string;
  api_key: string | null;
  embed_snippet: string;
};

export type AnalyticsOverview = {
  conversations: number;
  messages: number;
  leads: number;
  fallback_rate: number;
  documents_ready: number;
};
