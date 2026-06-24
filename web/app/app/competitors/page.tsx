"use client";

import { useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { KPIGrid, KPICardProps } from "@/components/shared/kpi-card";
import { DataTable } from "@/components/shared/data-table";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardFooter, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ColumnDef } from "@tanstack/react-table";
import { Search, AlertCircle, TrendingUp, Users, ArrowRight, MessageSquareReply, MapPin, Flag } from "lucide-react";

// Expanded rich mock data
const mockCompetitorMentions = [
  {
    id: "mention-1",
    competitor: "NoBroker",
    post_content: "NoBroker support is terrible. Been waiting 3 days for a response about a 2BHK in Sector 56.",
    sentiment: "Negative",
    complaint: "Support responsiveness",
    location: "Sector 56, Gurgaon",
    intent: "RENT",
    opportunity: "Very High",
    date: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
  },
  {
    id: "mention-2",
    competitor: "99acres",
    post_content: "Why are there so many fake listings on 99acres lately? I just want to find a genuine seller in Indiranagar.",
    sentiment: "Negative",
    complaint: "Fake/spam listings",
    location: "Indiranagar, Bangalore",
    intent: "BUY",
    opportunity: "High",
    date: new Date(Date.now() - 1000 * 60 * 60 * 15).toISOString(),
  },
  {
    id: "mention-3",
    competitor: "MagicBricks",
    post_content: "MagicBricks app keeps crashing when I try to upload photos of my property. So frustrating.",
    sentiment: "Negative",
    complaint: "App stability/Bugs",
    location: "Mumbai",
    intent: "SELL",
    opportunity: "Medium",
    date: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
  },
  {
    id: "mention-4",
    competitor: "Housing.com",
    post_content: "Honestly Housing.com's UI is pretty good, but their lead quality has dropped significantly this month.",
    sentiment: "Mixed",
    complaint: "Lead quality",
    location: "Delhi NCR",
    intent: "SELL",
    opportunity: "Medium",
    date: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
  },
  {
    id: "mention-5",
    competitor: "NoBroker",
    post_content: "Does anyone know a platform that actually verifies owners? NoBroker promised verified owners but half the calls are brokers.",
    sentiment: "Negative",
    complaint: "Trust/Verification",
    location: "Pune",
    intent: "RENT",
    opportunity: "Very High",
    date: new Date(Date.now() - 1000 * 60 * 60 * 72).toISOString(),
  }
];

export default function CompetitorsPage() {
  const [activeTab, setActiveTab] = useState("complaints");

  const kpiCards: KPICardProps[] = [
    { 
      label: "Total Mentions", 
      value: 124, 
      trend: { value: 12, direction: "up" },
      icon: Search 
    },
    { 
      label: "Dissatisfaction Signals", 
      value: 48, 
      trend: { value: 5, direction: "up" },
      icon: AlertCircle 
    },
    { 
      label: "High Intent Leads", 
      value: 15, 
      trend: { value: 30, direction: "up" },
      icon: TrendingUp 
    },
    { 
      label: "Competitors Tracked", 
      value: 4, 
      icon: Users 
    },
  ];

  const columns: ColumnDef<Record<string, unknown>>[] = [
    {
      key: "competitor",
      header: "Competitor",
      render: (row) => <span className="font-semibold text-primary">{String(row.competitor)}</span>,
    },
    {
      key: "post_content",
      header: "Mentioned Post",
      className: "max-w-[400px]",
      render: (row) => (
        <span className="text-sm block truncate" title={String(row.post_content)}>
          "{String(row.post_content)}"
        </span>
      ),
    },
    {
      key: "sentiment",
      header: "Sentiment",
      render: (row) => {
        const val = String(row.sentiment);
        return (
          <Badge variant={val === "Negative" ? "destructive" : val === "Mixed" ? "secondary" : "default"}>
            {val}
          </Badge>
        );
      }
    },
    {
      key: "complaint",
      header: "Complaint / Topic",
      render: (row) => <span className="text-sm font-medium">{String(row.complaint)}</span>,
    },
    {
      key: "intent",
      header: "Intent",
      render: (row) => <Badge variant="outline" className="text-xs">{String(row.intent)}</Badge>,
    },
    {
      key: "opportunity",
      header: "Opportunity",
      render: (row) => {
        const opp = String(row.opportunity);
        return (
          <Badge className={opp === "Very High" ? "bg-coral-500 text-white hover:bg-coral-600" : "bg-primary/10 text-primary hover:bg-primary/20"}>
            {opp}
          </Badge>
        );
      },
    },
    {
      key: "date",
      header: "Detected",
      render: (row) => {
        const date = new Date(String(row.date));
        return <span className="text-xs text-muted-foreground">{date.toLocaleDateString()} {date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>;
      }
    }
  ];

  const negativeMentions = mockCompetitorMentions.filter(m => m.sentiment === "Negative");

  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <PageHeader 
          title="Competitor Intelligence" 
          description="Automatically monitor competitor mentions and detect dissatisfaction signals to find high-intent leads." 
        />
        <Button className="bg-coral-500 hover:bg-coral-600 text-white shrink-0">
          Add Competitor
        </Button>
      </div>

      <KPIGrid cards={kpiCards} columns={4} className="grid-cols-2 lg:grid-cols-4" />

      {/* Sentiment Overview Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <Card className="col-span-1 md:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg">Sentiment Breakdown</CardTitle>
            <CardDescription>Mentions over the last 30 days</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1 text-sm">
                  <span className="font-medium">Negative (Complaints)</span>
                  <span className="text-muted-foreground">38%</span>
                </div>
                <Progress value={38} className="h-2.5 bg-muted [&>div]:bg-destructive" />
              </div>
              <div>
                <div className="flex justify-between mb-1 text-sm">
                  <span className="font-medium">Neutral / Mixed</span>
                  <span className="text-muted-foreground">45%</span>
                </div>
                <Progress value={45} className="h-2.5 bg-muted [&>div]:bg-slate-400" />
              </div>
              <div>
                <div className="flex justify-between mb-1 text-sm">
                  <span className="font-medium">Positive</span>
                  <span className="text-muted-foreground">17%</span>
                </div>
                <Progress value={17} className="h-2.5 bg-muted [&>div]:bg-success" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-1">
          <CardHeader>
            <CardTitle className="text-lg">Top Complaints</CardTitle>
            <CardDescription>Recurring themes</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <div className="flex justify-between items-center text-sm">
              <span className="font-medium text-destructive">Support Responsiveness</span>
              <Badge variant="secondary">18 mentions</Badge>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="font-medium text-destructive">Fake Listings</span>
              <Badge variant="secondary">12 mentions</Badge>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="font-medium text-destructive">High Brokerage</span>
              <Badge variant="secondary">9 mentions</Badge>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="font-medium text-destructive">App Stability</span>
              <Badge variant="secondary">4 mentions</Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="complaints" className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            Signals & Opportunities
            <Badge variant="destructive" className="ml-1 px-1.5 py-0 min-w-[20px] h-5 flex items-center justify-center">
              {negativeMentions.length}
            </Badge>
          </TabsTrigger>
          <TabsTrigger value="mentions">
            All Mentions
            <Badge variant="secondary" className="ml-1.5">{mockCompetitorMentions.length}</Badge>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="complaints" className="mt-5">
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
            {negativeMentions.map(mention => (
              <Card key={mention.id} className="flex flex-col shadow-sm border-l-4 border-l-destructive hover:shadow-md transition-all">
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-start mb-2">
                    <Badge variant="outline" className="bg-destructive/5 text-destructive font-bold border-destructive/20">
                      {mention.competitor}
                    </Badge>
                    <Badge className={mention.opportunity === "Very High" ? "bg-coral-500 hover:bg-coral-600" : ""}>
                      {mention.opportunity} Opp
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mt-2">
                    <Flag className="h-3.5 w-3.5" />
                    <span className="font-medium text-foreground">{mention.complaint}</span>
                  </div>
                </CardHeader>
                <CardContent className="flex-1">
                  <div className="relative">
                    <MessageSquareReply className="absolute left-3 top-3 h-4 w-4 text-muted-foreground/50" />
                    <div className="bg-muted/50 p-3 pl-9 rounded-md text-sm italic text-foreground/90 leading-relaxed border border-border/50">
                      "{mention.post_content}"
                    </div>
                  </div>
                  <div className="flex items-center gap-4 mt-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1.5">
                      <MapPin className="h-3.5 w-3.5" />
                      {mention.location}
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Badge variant="secondary" className="text-[10px] px-1.5 uppercase tracking-wider">{mention.intent}</Badge>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="pt-3 border-t bg-muted/20">
                  <Button variant="default" size="sm" className="w-full gap-2 shadow-sm">
                    Draft Reply
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="mentions" className="mt-5">
          <Card>
            <CardContent className="p-0">
              <DataTable
                columns={columns}
                data={mockCompetitorMentions as unknown as Record<string, unknown>[]}
                emptyState={{
                  title: "No competitor mentions found",
                  description: "Competitor mentions will appear here when the scanner detects them.",
                }}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
