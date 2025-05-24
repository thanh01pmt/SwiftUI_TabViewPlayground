//
//  NewFeedbiew.swift
//  SwiftUI_TabViewPlayground
//
//  Created by Tony Pham on 24/5/25.
//

import SwiftUI

struct NewsFeedView: View {
    var body: some View {
        ZStack { // Sử dụng ZStack để đặt màu nền
            Color.blue.opacity(0.2).ignoresSafeArea() // Màu nền nhẹ
            VStack {
                Image(systemName: "newspaper.fill")
                    .font(.system(size: 60))
                    .foregroundColor(.blue)
                Text("Bảng Tin Tức")
                    .font(.title)
                    .padding()
                Text("Nơi cập nhật những thông tin nóng hổi nhất.")
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
            }
        }
    }
}

#Preview {
    NewsFeedView()
}
