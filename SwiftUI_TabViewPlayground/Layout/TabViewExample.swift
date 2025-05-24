//
//  TabView.swift
//  SwiftUI_TabViewPlayground
//
//  Created by Tony Pham on 24/5/25.
//

import SwiftUI

struct TabViewExample: View {
    var body: some View {
        TabView {
            // TAB 1: Màn hình "Home"
            Text("Đây là Màn hình Home")
                .tabItem { // Định nghĩa giao diện cho tab này
                    Label("Home", systemImage: "house.fill")
                }

            // TAB 2: Màn hình "Settings"
            Text("Đây là Màn hình Cài đặt")
                .tabItem { // Định nghĩa giao diện cho tab này
                    Label("Cài đặt", systemImage: "gearshape.fill")
                }

            // TAB 3: Màn hình "Profile"
            Text("Đây là Màn hình Hồ sơ")
                .tabItem { // Định nghĩa giao diện cho tab này
                    Label("Hồ sơ", systemImage: "person.crop.circle.fill")
                }
        }
    }
}

#Preview {
    TabViewExample()
}
