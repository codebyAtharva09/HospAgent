const { Client } = require('pg');

const connectionString = 'postgresql://postgres:Atharva@0211@haerufpnwtdqffsysuyd.supabase.co:5432/postgres';

const client = new Client({
  connectionString: connectionString,
});

async function fetchData() {
  try {
    await client.connect();
    console.log('Connected to Supabase database successfully!');
    const res = await client.query('SELECT * FROM predictions LIMIT 5');
    console.log('Sample data from predictions table:', res.rows);
  } catch (err) {
    console.error('Connection error:', err.message);
  } finally {
    await client.end();
  }
}

fetchData();
