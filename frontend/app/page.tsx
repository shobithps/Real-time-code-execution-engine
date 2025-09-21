"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Play, Copy, Trash2, Terminal, Code } from 'lucide-react';
import { cn } from '@/lib/utils';

const LANGUAGES = [
  { value: 'python', label: 'Python', extension: '.py' },
  { value: 'java', label: 'Java', extension: '.java' },
  { value: 'cpp', label: 'C++', extension: '.cpp' },
];

const SAMPLE_CODE = {
  python: `# Python Example
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print("Fibonacci sequence:")
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")`,
  java: `// Java Example
public class Main {
    public static void main(String[] args) {
        System.out.println("Fibonacci sequence:");
        for (int i = 0; i < 10; i++) {
            System.out.println("F(" + i + ") = " + fibonacci(i));
        }
    }
    
    static int fibonacci(int n) {
        if (n <= 1) return n;
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
}`,
  cpp: `// C++ Example
#include <iostream>
using namespace std;

int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main() {
    cout << "Fibonacci sequence:" << endl;
    for (int i = 0; i < 10; i++) {
        cout << "F(" << i << ") = " << fibonacci(i) << endl;
    }
    return 0;
}`,
};

export default function Home() {
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  const [code, setCode] = useState(SAMPLE_CODE.python);
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);

  const handleLanguageChange = (language: string) => {
    setSelectedLanguage(language);
    setCode(SAMPLE_CODE[language as keyof typeof SAMPLE_CODE] || '');
    setOutput('');
  };

  const handleRunCode = async () => {
  setIsRunning(true);
  setOutput("Submitting code to processing queue...");

  try {
    const response = await fetch("http://localhost:8000/submit-code", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        code,
        language: selectedLanguage,
        input_data: "",
        user_id: "frontend-user",
      }),
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const result = await response.json();

    setOutput(
      `✓ ${result.message}\n\n` +
      `Request ID: ${result.request_id}\n` +
      `Status: ${result.status}\n` +
      `Timestamp: ${result.timestamp}\n\n` +
      `Your code has been queued for processing in the Kafka broker.`
    );

    // Start polling for results
    const interval = setInterval(async () => {
      const res = await fetch(`http://localhost:8000/get-result/${result.request_id}`);
      const data = await res.json();

      if (data.status === "completed") {
        clearInterval(interval);
        setOutput(
          `Output:\n${data.output.stdout || ""}\n` +
          `Error:\n${data.output.stderr || ""}\n` +
          `Exit Code: ${data.output.returncode}\n`
        );
      }
    }, 2000); // poll every 2s

  } catch (error: any) {
    setOutput(`❌ Connection Error: ${error.message}`);
  } finally {
    setIsRunning(false);
  }
};


  const handleCopyCode = () => {
    navigator.clipboard.writeText(code);
  };

  const handleClearEditor = () => {
    setCode('');
    setOutput('');
  };

  const handleClearOutput = () => {
    setOutput('');
  };

  const selectedLang = LANGUAGES.find(lang => lang.value === selectedLanguage);

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <div className="border-b border-slate-800 bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Code className="h-6 w-6 text-blue-400" />
              <h1 className="text-xl font-semibold">Code Runner</h1>
            </div>
            <Badge variant="secondary" className="bg-slate-700 text-slate-300">
              {selectedLang?.label} {selectedLang?.extension}
            </Badge>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-4 gap-4 grid grid-cols-1 lg:grid-cols-2 min-h-[calc(100vh-80px)]">
        {/* Code Editor Section */}
        <Card className="bg-slate-800 border-slate-700 flex flex-col">
          <div className="flex items-center justify-between p-4 border-b border-slate-700">
            <div className="flex items-center gap-3">
              <Code className="h-4 w-4 text-slate-400" />
              <span className="text-sm font-medium text-slate-300">Editor</span>
            </div>
            <div className="flex items-center gap-2">
              <Select value={selectedLanguage} onValueChange={handleLanguageChange}>
                <SelectTrigger className="w-32 bg-slate-700 border-slate-600 text-slate-200">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-700 border-slate-600">
                  {LANGUAGES.map((lang) => (
                    <SelectItem key={lang.value} value={lang.value} className="text-slate-200 focus:bg-slate-600">
                      {lang.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                variant="outline"
                size="sm"
                onClick={handleCopyCode}
                className="border-slate-600 text-slate-300 hover:bg-slate-700"
              >
                <Copy className="h-3 w-3" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearEditor}
                className="border-slate-600 text-slate-300 hover:bg-slate-700"
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
          </div>
          <div className="flex-1 p-0">
            <Textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Write your code here..."
              className="w-full h-full min-h-[400px] resize-none border-0 bg-slate-900 text-slate-100 font-mono text-sm leading-relaxed focus-visible:ring-0 focus-visible:ring-offset-0"
            />
          </div>
          <div className="p-4 border-t border-slate-700">
            <Button 
              onClick={handleRunCode} 
              disabled={isRunning || !code.trim()}
              className="w-full bg-green-600 hover:bg-green-700 disabled:bg-slate-700"
            >
              <Play className={cn("h-4 w-4 mr-2", isRunning && "animate-spin")} />
              {isRunning ? 'Running...' : 'Run Code'}
            </Button>
          </div>
        </Card>

        {/* Output Console Section */}
        <Card className="bg-slate-800 border-slate-700 flex flex-col">
          <div className="flex items-center justify-between p-4 border-b border-slate-700">
            <div className="flex items-center gap-3">
              <Terminal className="h-4 w-4 text-slate-400" />
              <span className="text-sm font-medium text-slate-300">Output Console</span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleClearOutput}
              className="border-slate-600 text-slate-300 hover:bg-slate-700"
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
          <div className="flex-1 p-4">
            <div className="bg-slate-900 rounded-md p-4 h-full min-h-[400px] overflow-auto">
              <pre className="text-sm text-slate-300 font-mono whitespace-pre-wrap">
                {output || 'Click "Run Code" to see the output...'}
              </pre>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}