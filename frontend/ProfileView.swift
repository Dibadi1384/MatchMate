//
//  ProfileView.swift
//  MatchMate
//

import SwiftUI

struct ProfileView: View {
    @EnvironmentObject var appState: AppState
    @Environment(\.dismiss) var dismiss
    @State private var bio: String = ""
    @State private var ageText: String = ""
    @State private var pronouns: String = ""
    @State private var selectedImage: UIImage?
    @State private var showImagePicker = false
    @State private var saved = false

    private var profile: UserProfile? {
        appState.currentUserProfile
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                if let email = appState.currentUser?.email {
                    Text(email)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }

                Button(action: { showImagePicker = true }) {
                    Group {
                        if let img = selectedImage {
                            Image(uiImage: img)
                                .resizable()
                                .scaledToFill()
                        } else if let data = profile?.photoData, let img = UIImage(data: data) {
                            Image(uiImage: img)
                                .resizable()
                                .scaledToFill()
                        } else {
                            Image(systemName: "person.circle.fill")
                                .resizable()
                                .foregroundColor(.gray)
                        }
                    }
                    .frame(width: 120, height: 120)
                    .clipShape(Circle())
                }
                .padding(.vertical, 8)

                Text("Bio")
                    .font(.caption)
                    .foregroundColor(.secondary)
                TextField("Bio", text: $bio, axis: .vertical)
                    .lineLimit(3...6)
                    .textFieldStyle(.roundedBorder)

                Text("Age")
                    .font(.caption)
                    .foregroundColor(.secondary)
                TextField("Age", text: $ageText)
                    .keyboardType(.numberPad)
                    .textFieldStyle(.roundedBorder)

                Text("Pronouns")
                    .font(.caption)
                    .foregroundColor(.secondary)
                TextField("Pronouns", text: $pronouns)
                    .textFieldStyle(.roundedBorder)

                Button(action: save) {
                    Text("Save")
                        .fontWeight(.semibold)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.accentColor)
                        .foregroundColor(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .padding(.top, 8)

                if saved {
                    Text("Saved.")
                        .font(.caption)
                        .foregroundColor(.green)
                }
            }
            .padding(24)
        }
        .navigationTitle("Profile")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear { loadProfile() }
        .sheet(isPresented: $showImagePicker) {
            ImagePicker(image: $selectedImage)
        }
    }

    private func loadProfile() {
        guard let p = profile else { return }
        bio = p.bio
        ageText = p.age.map { String($0) } ?? ""
        pronouns = p.pronouns ?? ""
    }

    private func save() {
        guard let user = appState.currentUser else { return }
        var photoData: Data?
        if let img = selectedImage {
            photoData = img.jpegData(compressionQuality: 0.7)
        } else if let data = profile?.photoData {
            photoData = data
        }
        let updated = UserProfile(
            userId: user.id,
            photoData: photoData,
            bio: bio,
            age: Int(ageText),
            pronouns: pronouns.isEmpty ? nil : pronouns
        )
        appState.updateProfile(updated)
        saved = true
    }
}

#Preview {
    NavigationStack {
        ProfileView()
            .environmentObject({
                let a = AppState()
                a.currentUser = User(id: "1", email: "u@ex.com")
                a.currentUserProfile = UserProfile(userId: "1", bio: "Hello", age: 28, pronouns: "they/them")
                return a
            }())
    }
}
