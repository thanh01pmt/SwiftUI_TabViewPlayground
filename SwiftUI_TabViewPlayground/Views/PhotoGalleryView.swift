//
//  PhotoGallaryView.swift
//  SwiftUI_TabViewPlayground
//
//  Created by Tony Pham on 24/5/25.
//

import SwiftUI

struct PhotoGalleryView: View {
    var body: some View {
        ZStack {
            Color.green.opacity(0.2).ignoresSafeArea()
            VStack {
                Image(systemName: "photo.on.rectangle.angled")
                    .font(.system(size: 60))
                    .foregroundColor(.green)
                Text("Thư Viện Ảnh")
                    .font(.title)
                    .padding()
                Text("Khám phá những khoảnh khắc tuyệt vời được ghi lại.")
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
            }
        }
    }
}

#Preview {
    PhotoGalleryView()
}
