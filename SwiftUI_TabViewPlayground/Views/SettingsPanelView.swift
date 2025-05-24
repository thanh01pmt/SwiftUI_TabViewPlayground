//
//  SettingPanelView.swift
//  SwiftUI_TabViewPlayground
//
//  Created by Tony Pham on 24/5/25.
//

import SwiftUI

struct SettingsPanelView: View {
    var body: some View {
        ZStack {
            Color.orange.opacity(0.2).ignoresSafeArea()
            VStack {
                Image(systemName: "slider.horizontal.3")
                    .font(.system(size: 60))
                    .foregroundColor(.orange)
                Text("Bảng Cài Đặt")
                    .font(.title)
                    .padding()
                Text("Tùy chỉnh ứng dụng theo sở thích của bạn.")
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
            }
        }
    }
}

#Preview {
    SettingsPanelView()
}
