'use client'

import { useState, useEffect } from 'react'
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Input } from '@/components/ui/input'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface Event {
  step: number
  total_loss: number
  outcome: string
}

interface RunDetailDrawerProps {
  open: boolean
  onClose: () => void
  runId: string | null
}

export function RunDetailDrawer({ open, onClose, runId }: RunDetailDrawerProps) {
  const [events, setEvents] = useState<Event[]>([])
  const [search, setSearch] = useState('')

  useEffect(() => {
    if (runId) {
      fetch(`http://localhost:8000/api/log/${runId}`)
        .then(r => r.json())
        .then(data => setEvents(data.events))
    }
  }, [runId])

  const filteredEvents = events.filter(e => 
    search === '' || JSON.stringify(e).toLowerCase().includes(search.toLowerCase())
  )

  return (
    <Sheet open={open} onOpenChange={onClose}>
      <SheetContent className="w-[600px] sm:w-[800px]">
        <SheetHeader>
          <SheetTitle>Run Details: {runId}</SheetTitle>
        </SheetHeader>
        
        <div className="space-y-6 mt-6">
          {/* Loss Timeline */}
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={events}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="step" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="total_loss" stroke="#1D4ED8" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Event Search */}
          <Input
            placeholder="Search events..."
            value={search}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearch(e.target.value)}
          />

          {/* Event List */}
          <div className="h-[400px] overflow-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Step</TableHead>
                  <TableHead>Total Loss</TableHead>
                  <TableHead>Outcome</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredEvents.map((event, i) => (
                  <TableRow key={i}>
                    <TableCell>{event.step}</TableCell>
                    <TableCell>{event.total_loss.toFixed(3)}</TableCell>
                    <TableCell>{event.outcome}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
