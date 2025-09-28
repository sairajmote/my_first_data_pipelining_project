import { createClient } from '@supabase/supabase-js';

// Supabase configuration - Updated with new database
const supabaseUrl = 'https://ppabpyixlqdjjvrewieh.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBwYWJweWl4bHFkamp2cmV3aWVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkwODc3MDYsImV4cCI6MjA3NDY2MzcwNn0.EW3R9N4tZfgkukx5-N-FBGssC7aqCQlaeKcVWXfDrOQ';

export const supabase = createClient(supabaseUrl, supabaseKey);

// Database table names
export const TABLES = {
  SENSOR_READINGS: 'sensor_readings',
  ALERTS: 'alerts'
};
