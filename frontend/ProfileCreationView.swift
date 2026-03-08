//
//  ProfileCreationView.swift
//  MatchMate
//

import SwiftUI

struct ProfileCreationView: View {
    @Binding var path: NavigationPath
    @EnvironmentObject var appState: AppState
    @State private var bio = ""
    @State private var ageText = ""
    @State private var pronouns = ""
    @State private var selectedImage: UIImage?
    @State private var showImagePicker = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Create your profile")
                    .font(.title2)
                    .fontWeight(.bold)

                Button(action: { showImagePicker = true }) {
                    Group {
                        if let img = selectedImage {
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

                TextField("Bio", text: $bio, axis: .vertical)
                    .lineLimit(3...6)
                    .textFieldStyle(.roundedBorder)

                TextField("Age", text: $ageText)
                    .keyboardType(.numberPad)
                    .textFieldStyle(.roundedBorder)

                TextField("Pronouns (e.g. she/her)", text: $pronouns)
                    .textFieldStyle(.roundedBorder)

                Button(action: submit) {
                    Text("Continue")
                        .fontWeight(.semibold)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.accentColor)
                        .foregroundColor(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .padding(.top, 8)
            }
            .padding(24)
        }
        .navigationTitle("Profile")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showImagePicker) {
            ImagePicker(image: $selectedImage)
        }
    }

    private func submit() {
        let age = Int(ageText)
        let userId = appState.currentUser?.id ?? UUID().uuidString
        var photoData: Data?
        if let img = selectedImage {
            photoData = img.jpegData(compressionQuality: 0.7)
        }
        let profile = UserProfile(
            userId: userId,
            photoData: photoData,
            bio: bio,
            age: age,
            pronouns: pronouns.isEmpty ? nil : pronouns
        )
        appState.setPendingProfile(profile)

        #if DEBUG
        path.append(AuthStep.dataUpload)
        #else
        appState.finishSignUp()
        #endif
    }
}

// Simple image picker wrapper
struct ImagePicker: UIViewControllerRepresentable {
    @Binding var image: UIImage?
    @Environment(\.dismiss) var dismiss

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        picker.sourceType = .photoLibrary
        return picker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: ImagePicker
        init(_ parent: ImagePicker) { self.parent = parent }
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            parent.image = info[.originalImage] as? UIImage
            parent.dismiss()
        }
        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            parent.dismiss()
        }
    }
}

#Preview {
    NavigationStack {
        ProfileCreationView(path: .constant(NavigationPath()))
            .environmentObject(AppState())
    }
}
