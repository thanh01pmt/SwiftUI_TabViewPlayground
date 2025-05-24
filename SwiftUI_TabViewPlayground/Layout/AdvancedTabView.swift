//
//  AdvancedTabView.swift
//  SwiftUI_TabViewPlayground
//
//  Created by Tony Pham on 24/5/25.
//

import SwiftUI

struct AdvancedTabView: View {
    // Sử dụng enum để quản lý các tab một cách rõ ràng hơn
    enum AppTab: Int, CaseIterable, Identifiable {
        case news = 0
        case photos = 1
        case settings = 2

        var id: Int { self.rawValue }

        // Tiện ích để lấy tên và icon cho mỗi tab
        var title: String {
            switch self {
            case .news: return "Tin Tức"
            case .photos: return "Ảnh"
            case .settings: return "Cài Đặt"
            }
        }

        var systemImage: String {
            switch self {
            case .news: return "newspaper.fill"
            case .photos: return "photo.on.rectangle.angled"
            case .settings: return "slider.horizontal.3"
            }
        }
    }

    @State private var selectedTab: AppTab = .news // Tab mặc định là Tin tức
    private let totalTabs = AppTab.allCases.count // Tổng số tab

    var body: some View {
        VStack {
            TabView(selection: $selectedTab) {
                NewsFeedView() // Custom View cho Tab 1
                    .tabItem {
                        Label(AppTab.news.title, systemImage: AppTab.news.systemImage)
                    }
                    .tag(AppTab.news) // Sử dụng enum làm tag

                PhotoGalleryView() // Custom View cho Tab 2
                    .tabItem {
                        Label(AppTab.photos.title, systemImage: AppTab.photos.systemImage)
                    }
                    .tag(AppTab.photos)

                SettingsPanelView() // Custom View cho Tab 3
                    .tabItem {
                        Label(AppTab.settings.title, systemImage: AppTab.settings.systemImage)
                    }
                    .tag(AppTab.settings)
            }

            // Nút "Next Tab"
            Button(action: {
                // Lấy rawValue (số nguyên) của tab hiện tại
                let currentTabIndex = selectedTab.rawValue
                // Tính toán tab tiếp theo, quay vòng nếu đến cuối
                let nextTabIndex = (currentTabIndex + 1) % totalTabs
                // Cập nhật selectedTab bằng AppTab tương ứng với index mới
                if let nextTab = AppTab(rawValue: nextTabIndex) {
                    selectedTab = nextTab
                }
            }) {
                HStack {
                    Text("Chuyển Tab Tiếp Theo")
                    Image(systemName: "arrow.right.circle.fill")
                }
                .padding()
                .foregroundColor(.white)
                .background(Color.purple)
                .cornerRadius(10)
            }
            .padding(.bottom) // Thêm padding cho nút
        }
    }
}


#Preview {
    AdvancedTabView()
}
