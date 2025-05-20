'use client'

import Image from "next/image";
import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { RunDetailDrawer } from '@/components/run-detail-drawer'

interface LogFile {
  name: string
}

interface Run {
  run: string
  total_loss: number
  success: number
}

interface Summary {
  SuccessRate: number
  EDL: number
  'CVaR@90': number
  BreachRate: number
}

export default function Home() {
  const [logs, setLogs] = useState<LogFile[]>([])
  const [selected, setSelected] = useState<string[]>([])
  const [summary, setSummary] = useState<Summary | null>(null)
  const [runs, setRuns] = useState<Run[]>([])
  const [search, setSearch] = useState('')
  const [alpha, setAlpha] = useState(0.9)
  const [selectedRun, setSelectedRun] = useState<string | null>(null)

  useEffect(() => {
    const url = search
      ? `http://localhost:8000/api/logs?search=${encodeURIComponent(search)}`
      : 'http://localhost:8000/api/logs'
    fetch(url)
      .then(r => r.json())
      .then(data => setLogs(data.map((name: string) => ({ name }))))
  }, [search])

  const toggle = (name: string) => {
    setSelected(s =>
      s.includes(name) ? s.filter(x => x !== name) : [...s, name]
    )
  }

  const compute = () => {
    const params = new URLSearchParams()
    if (selected.length) params.set('files', selected.join(','))
    params.set('alpha', alpha.toString())
    fetch('http://localhost:8000/api/metrics?' + params.toString())
      .then(r => r.json())
      .then(data => {
        setSummary(data.summary)
        setRuns(data.runs)
      })
  }

  const selectAll = () => {
    setSelected(logs.map(l => l.name))
  }

  const invertSelection = () => {
    setSelected(logs.map(l => l.name).filter(n => !selected.includes(n)))
  }

  return (
    <main className="container mx-auto p-6">
      <h1 className="text-4xl font-bold mb-8">RiskDash</h1>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Select Logs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <input
                type="text"
                placeholder="Search logs..."
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="flex items-center space-x-2">
              <Button onClick={selectAll} variant="outline" size="sm">
                Select All
              </Button>
              <Button onClick={invertSelection} variant="outline" size="sm">
                Invert Selection
              </Button>
            </div>
            <div className="grid grid-cols-3 gap-4">
              {logs.map(({ name }) => (
                <div key={name} className="flex items-center space-x-2">
                  <Checkbox
                    id={name}
                    checked={selected.includes(name)}
                    onCheckedChange={() => toggle(name)}
                  />
                  <Label htmlFor={name}>{name}</Label>
                </div>
              ))}
            </div>
            <div className="space-y-2">
              <Label>CVaR α</Label>
              <div className="flex items-center space-x-2">
                <input
                  type="range"
                  min="0.5"
                  max="0.99"
                  step="0.01"
                  value={alpha}
                  onChange={(e) => setAlpha(parseFloat(e.target.value))}
                  className="flex h-10 w-full"
                />
                <span className="text-sm">{alpha.toFixed(2)}</span>
              </div>
            </div>
            <Button onClick={compute} className="w-full">
              Compute Metrics
            </Button>
          </div>
        </CardContent>
      </Card>

      {summary && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  {Object.keys(summary).map(k => (
                    <TableHead key={k}>{k}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  {Object.values(summary).map((v, i) => (
                    <TableCell key={i}>{(v as number).toFixed(3)}</TableCell>
                  ))}
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {runs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Success vs. Loss</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="total_loss" 
                    name="Loss" 
                    label={{ value: 'Total Loss', position: 'bottom' }}
                  />
                  <YAxis 
                    dataKey="success" 
                    name="Success" 
                    label={{ value: 'Success', angle: -90, position: 'left' }}
                  />
                  <Tooltip 
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload;
                        return (
                          <div className="bg-white p-2 border rounded shadow-lg">
                            <p className="text-sm font-medium">{data.run}</p>
                            <p className="text-sm">Loss: {data.total_loss.toFixed(3)}</p>
                            <p className="text-sm">Success: {data.success ? 'Yes' : 'No'}</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Scatter 
                    data={runs} 
                    fill="#1D4ED8"
                    onClick={(data: any) => {
                      setSelectedRun(data.payload.run);
                    }}
                  />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}
      <RunDetailDrawer
        open={selectedRun !== null}
        onClose={() => setSelectedRun(null)}
        runId={selectedRun}
      />
    </main>
  )
}
