import { NextResponse } from 'next/server';

export async function GET() {
  // Basic health check
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
  };

  return NextResponse.json(health);
}
