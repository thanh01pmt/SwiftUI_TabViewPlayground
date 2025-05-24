//
//  ControllableTabView.swift
//  SwiftUI_TabViewPlayground
//
//  Created by Tony Pham on 24/5/25.
//

import SwiftUI

struct ControllableTabView: View {
    @State private var selectedTab: Int = 0 // Tab đầu tiên (tag 0) sẽ được chọn mặc định

    var body: some View {
        VStack {
            TabView(selection: $selectedTab) { // Liên kết với selectedTab
                Text("Nội dung Tab 1")
                    .tabItem {
                        Label("Tab 1", systemImage: "1.circle")
                    }
                    .tag(0) // Gán tag 0

                Text("Nội dung Tab 2")
                    .tabItem {
                        Label("Tab 2", systemImage: "2.circle")
                    }
                    .tag(1) // Gán tag 1
            }

            // Ví dụ: Nút để chuyển tab
            Button("Chuyển đến Tab 2") {
                selectedTab = 1 // Thay đổi giá trị selectedTab sẽ tự động chuyển tab
            }
            .padding()
        }
    }
}

#Preview {
    ControllableTabView()
}
