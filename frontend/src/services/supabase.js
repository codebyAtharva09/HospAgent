import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || 'https://your-project-id.supabase.co'
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || 'your-anon-key-here'

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// API functions for fetching data
export const getPredictionsHistory = async () => {
  const { data, error } = await supabase
    .from('predictions')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(50)

  if (error) {
    console.error('Error fetching predictions:', error)
    return []
  }

  return data
}

export const getStaffRecommendationsHistory = async () => {
  const { data, error } = await supabase
    .from('recommendations')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(50)

  if (error) {
    console.error('Error fetching staff recommendations:', error)
    return []
  }

  return data
}

export const getInventoryRecommendationsHistory = async () => {
  const { data, error } = await supabase
    .from('recommendations')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(50)

  if (error) {
    console.error('Error fetching inventory recommendations:', error)
    return []
  }

  return data
}

export const getRecommendationsHistory = async () => {
  const { data, error } = await supabase
    .from('recommendations')
    .select(`
      *,
      predictions (
        date,
        predicted_patients,
        aqi,
        event_type
      )
    `)
    .order('created_at', { ascending: false })
    .limit(50)

  if (error) {
    console.error('Error fetching recommendations:', error)
    return []
  }

  return data
}

export const getAdvisoriesHistory = async () => {
  const { data, error } = await supabase
    .from('advisories')
    .select(`
      *,
      predictions (
        date,
        predicted_patients,
        aqi,
        event_type
      )
    `)
    .order('created_at', { ascending: false })
    .limit(50)

  if (error) {
    console.error('Error fetching advisories:', error)
    return []
  }

  return data
}

// Real-time subscriptions
export const subscribeToPredictions = (callback) => {
  return supabase
    .channel('predictions_changes')
    .on('postgres_changes', {
      event: '*',
      schema: 'public',
      table: 'predictions'
    }, callback)
    .subscribe()
}

export const subscribeToRecommendations = (callback) => {
  return supabase
    .channel('recommendations_changes')
    .on('postgres_changes', {
      event: '*',
      schema: 'public',
      table: 'recommendations'
    }, callback)
    .subscribe()
}

export const subscribeToAdvisories = (callback) => {
  return supabase
    .channel('advisories_changes')
    .on('postgres_changes', {
      event: '*',
      schema: 'public',
      table: 'advisories'
    }, callback)
    .subscribe()
}
