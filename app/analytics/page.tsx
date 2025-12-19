'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#6366f1'];

export default function AnalyticsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState<any>(null);
  const [geography, setGeography] = useState<any>(null);
  const [googleAds, setGoogleAds] = useState<any>(null);
  const [traffic, setTraffic] = useState<any>(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const [overviewRes, geoRes, adsRes, trafficRes] = await Promise.all([
        fetch('/api/analytics/overview'),
        fetch('/api/analytics/geography'),
        fetch('/api/analytics/google-ads'),
        fetch('/api/analytics/traffic')
      ]);

      const [overviewData, geoData, adsData, trafficData] = await Promise.all([
        overviewRes.json(),
        geoRes.json(),
        adsRes.json(),
        trafficRes.json()
      ]);

      setOverview(overviewData.overview);
      setGeography(geoData);
      setGoogleAds(adsData);
      setTraffic(trafficData);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">加载数据分析...</p>
        </div>
      </div>
    );
  }

  const formatNumber = (num: number) => new Intl.NumberFormat().format(num);

  // Prepare customer type pie chart data
  const customerTypePieData = googleAds?.customerTypes?.map((item: any) => ({
    name: item.type === 'new_customer' ? '🔥 新客户' : item.type === 'no_ads' ? '⭕ 无广告' : '老客户',
    value: item.count
  })) || [];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                onClick={() => router.push('/')}
                variant="ghost"
                className="text-white hover:bg-white/20"
              >
                ← 返回主页
              </Button>
              <div>
                <h1 className="text-3xl font-extrabold">📊 数据分析中心</h1>
                <p className="text-purple-100 text-sm mt-1">
                  全面分析店铺数据，挖掘潜在客户
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
            <CardHeader>
              <CardTitle className="text-lg">总店铺数</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">{formatNumber(overview?.total_stores || 0)}</div>
              <p className="text-purple-100 text-sm mt-2">覆盖{overview?.total_countries || 0}个国家</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-pink-500 to-pink-600 text-white">
            <CardHeader>
              <CardTitle className="text-lg">🔥 新客户</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">{formatNumber(overview?.new_customers || 0)}</div>
              <p className="text-pink-100 text-sm mt-2">豆豆的目标客户</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
            <CardHeader>
              <CardTitle className="text-lg">已检查店铺</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">{formatNumber(overview?.checked_stores || 0)}</div>
              <p className="text-green-100 text-sm mt-2">今日检查: {overview?.today_checked || 0}</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
            <CardHeader>
              <CardTitle className="text-lg">有广告店铺</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">{formatNumber(overview?.stores_with_ads || 0)}</div>
              <p className="text-orange-100 text-sm mt-2">总访问量: {formatNumber(overview?.total_visits || 0)}</p>
            </CardContent>
          </Card>
        </div>

        {/* Charts Row 1: Customer Type & Province Distribution */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>客户类型分布</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={customerTypePieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${percent ? (percent * 100).toFixed(0) : 0}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {customerTypePieData.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>各省份新客户分布 (中国)</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={googleAds?.provinceDistribution?.slice(0, 10) || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="province" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8b5cf6" name="新客户数" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Charts Row 2: Traffic Distribution & Top Cities */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>访问量分布</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={traffic?.trafficRanges || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="range" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="stores" fill="#10b981" name="店铺数" />
                  <Bar dataKey="newCustomers" fill="#f59e0b" name="新客户数" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>TOP 10 城市</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={geography?.cities?.slice(0, 10) || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="stores" fill="#ec4899" name="店铺数" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        {googleAds?.recentActivity && googleAds?.recentActivity.length > 0 && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>近7天检查活动</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={googleAds?.recentActivity || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="checked" stroke="#8b5cf6" name="检查数量" />
                  <Line type="monotone" dataKey="newCustomers" stroke="#f59e0b" name="新客户发现" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {/* Priority Targets Table */}
        {traffic?.priorityTargets && traffic?.priorityTargets.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>🎯 优先目标客户 (高访问量新客户)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">店铺名</th>
                      <th className="text-left p-2">位置</th>
                      <th className="text-right p-2">月访问量</th>
                      <th className="text-right p-2">广告数</th>
                      <th className="text-right p-2">员工数</th>
                      <th className="text-center p-2">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    {traffic?.priorityTargets?.slice(0, 20).map((store: any) => (
                      <tr key={store.id} className="border-b hover:bg-gray-50 dark:hover:bg-gray-800">
                        <td className="p-2 font-medium">{store.name}</td>
                        <td className="p-2 text-gray-600 dark:text-gray-400">{store.location}</td>
                        <td className="p-2 text-right">{formatNumber(store.visits)}</td>
                        <td className="p-2 text-right">{store.adCount}</td>
                        <td className="p-2 text-right">{store.employees}</td>
                        <td className="p-2 text-center">
                          <Button
                            size="sm"
                            onClick={() => router.push(`/store/${store.id}`)}
                            className="bg-purple-600 hover:bg-purple-700"
                          >
                            查看详情
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
